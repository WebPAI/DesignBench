"""
AST Edit Similarity Calculator for Frontend Code
Supports: React (.jsx), Angular (.angular), HTML (.html), Vue (.vue)
"""

import subprocess
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import difflib
from collections import Counter
import math


@dataclass
class ASTNode:
    """Simplified AST node representation"""
    type: str
    value: Any
    children: List['ASTNode']
    attributes: Dict[str, Any]

    def __hash__(self):
        return hash((self.type, str(self.value), tuple(self.attributes.items())))


class CodeBLEUCalculator:
    """Calculate BLEU and CodeBLEU scores for code similarity"""

    @staticmethod
    def compute_bleu(reference: str, hypothesis: str, max_n: int = 4) -> Dict[str, float]:
        """
        Compute BLEU score (n-gram based)

        Args:
            reference: Ground truth code
            hypothesis: Predicted code
            max_n: Maximum n-gram size (default 4)

        Returns:
            Dictionary with BLEU scores
        """
        ref_tokens = CodeBLEUCalculator._tokenize_code(reference)
        hyp_tokens = CodeBLEUCalculator._tokenize_code(hypothesis)

        # Calculate n-gram precisions
        precisions = []
        for n in range(1, max_n + 1):
            ref_ngrams = CodeBLEUCalculator._get_ngrams(ref_tokens, n)
            hyp_ngrams = CodeBLEUCalculator._get_ngrams(hyp_tokens, n)

            if not hyp_ngrams:
                precisions.append(0.0)
                continue

            # Count matches
            matches = 0
            for ngram in hyp_ngrams:
                if ngram in ref_ngrams:
                    matches += min(hyp_ngrams[ngram], ref_ngrams[ngram])

            precision = matches / sum(hyp_ngrams.values()) if hyp_ngrams else 0.0
            precisions.append(precision)

        # Brevity penalty
        ref_len = len(ref_tokens)
        hyp_len = len(hyp_tokens)

        if hyp_len > ref_len:
            bp = 1.0
        else:
            bp = math.exp(1 - ref_len / hyp_len) if hyp_len > 0 else 0.0

        # Geometric mean of precisions
        if all(p > 0 for p in precisions):
            geo_mean = math.exp(sum(math.log(p) for p in precisions) / len(precisions))
        else:
            geo_mean = 0.0

        bleu = bp * geo_mean

        return {
            'bleu': round(bleu, 4),
            'bleu-1': round(precisions[0], 4),
            'bleu-2': round(precisions[1] if len(precisions) > 1 else 0.0, 4),
            'bleu-3': round(precisions[2] if len(precisions) > 2 else 0.0, 4),
            'bleu-4': round(precisions[3] if len(precisions) > 3 else 0.0, 4),
            'bp': round(bp, 4)
        }

    @staticmethod
    def compute_codebleu(
            reference: str,
            hypothesis: str,
            reference_ast: Dict = None,
            hypothesis_ast: Dict = None,
            weights: Tuple[float, float, float, float] = (0.25, 0.25, 0.25, 0.25)
    ) -> Dict[str, float]:
        """
        Compute CodeBLEU score

        Args:
            reference: Ground truth code
            hypothesis: Predicted code
            reference_ast: AST of reference code (optional)
            hypothesis_ast: AST of hypothesis code (optional)
            weights: (ngram_weight, weighted_ngram_weight, syntax_weight, dataflow_weight)

        Returns:
            Dictionary with CodeBLEU scores
        """
        # 1. N-gram match (BLEU)
        bleu_scores = CodeBLEUCalculator.compute_bleu(reference, hypothesis)
        ngram_match = bleu_scores['bleu']

        # 2. Weighted n-gram match (considering keywords)
        weighted_ngram = CodeBLEUCalculator._weighted_ngram_match(reference, hypothesis)

        # 3. Syntax match (AST-based)
        if reference_ast and hypothesis_ast:
            syntax_match = CodeBLEUCalculator._syntax_match(reference_ast, hypothesis_ast)
        else:
            syntax_match = 0.0

        # 4. Dataflow match (variable usage patterns)
        dataflow_match = CodeBLEUCalculator._dataflow_match(reference, hypothesis)

        # Combined CodeBLEU score
        codebleu = (
                weights[0] * ngram_match +
                weights[1] * weighted_ngram +
                weights[2] * syntax_match +
                weights[3] * dataflow_match
        )

        return {
            'codebleu': round(codebleu, 4),
            'ngram_match': round(ngram_match, 4),
            'weighted_ngram_match': round(weighted_ngram, 4),
            'syntax_match': round(syntax_match, 4),
            'dataflow_match': round(dataflow_match, 4)
        }

    @staticmethod
    def _tokenize_code(code: str) -> List[str]:
        """Tokenize code into tokens"""
        import re
        # Simple tokenization: split by whitespace and punctuation
        tokens = re.findall(r'\w+|[^\w\s]', code)
        return [t for t in tokens if t.strip()]

    @staticmethod
    def _get_ngrams(tokens: List[str], n: int) -> Counter:
        """Get n-grams from token list"""
        ngrams = Counter()
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i:i + n])
            ngrams[ngram] += 1
        return ngrams

    @staticmethod
    def _weighted_ngram_match(reference: str, hypothesis: str) -> float:
        """
        Weighted n-gram match giving higher weight to keywords
        """
        keywords = {
            'function', 'const', 'let', 'var', 'return', 'if', 'else',
            'className', 'onClick', 'useState', 'useEffect', 'import', 'export',
            'class', 'extends', 'render', 'props', 'state'
        }

        ref_tokens = CodeBLEUCalculator._tokenize_code(reference)
        hyp_tokens = CodeBLEUCalculator._tokenize_code(hypothesis)

        # Weight tokens
        ref_weighted = Counter()
        hyp_weighted = Counter()

        for token in ref_tokens:
            weight = 2.0 if token in keywords else 1.0
            ref_weighted[token] += weight

        for token in hyp_tokens:
            weight = 2.0 if token in keywords else 1.0
            hyp_weighted[token] += weight

        # Calculate weighted overlap
        matches = 0.0
        for token in hyp_weighted:
            if token in ref_weighted:
                matches += min(hyp_weighted[token], ref_weighted[token])

        total = sum(hyp_weighted.values())

        return matches / total if total > 0 else 0.0

    @staticmethod
    def _syntax_match(ast1: Dict, ast2: Dict) -> float:
        """
        Calculate syntax match based on AST similarity
        """

        def get_node_types(ast, types=None):
            if types is None:
                types = []
            if isinstance(ast, dict):
                if 'type' in ast:
                    types.append(ast['type'])
                for value in ast.values():
                    get_node_types(value, types)
            elif isinstance(ast, list):
                for item in ast:
                    get_node_types(item, types)
            return types

        types1 = get_node_types(ast1)
        types2 = get_node_types(ast2)

        if not types1 and not types2:
            return 1.0

        # Calculate Jaccard similarity
        set1 = Counter(types1)
        set2 = Counter(types2)

        intersection = sum((set1 & set2).values())
        union = sum((set1 | set2).values())

        return intersection / union if union > 0 else 0.0

    @staticmethod
    def _dataflow_match(reference: str, hypothesis: str) -> float:
        """
        Calculate dataflow match based on variable usage patterns
        """
        import re

        # Extract variable declarations and usages
        def extract_dataflow(code):
            # Find variable declarations
            declarations = set(re.findall(r'(?:const|let|var)\s+(\w+)', code))
            # Find function calls
            function_calls = set(re.findall(r'(\w+)\s*\(', code))
            # Find property accesses
            properties = set(re.findall(r'\.(\w+)', code))

            return declarations, function_calls, properties

        ref_decl, ref_calls, ref_props = extract_dataflow(reference)
        hyp_decl, hyp_calls, hyp_props = extract_dataflow(hypothesis)

        # Calculate similarity for each category
        def jaccard(set1, set2):
            if not set1 and not set2:
                return 1.0
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            return intersection / union if union > 0 else 0.0

        decl_sim = jaccard(ref_decl, hyp_decl)
        calls_sim = jaccard(ref_calls, hyp_calls)
        props_sim = jaccard(ref_props, hyp_props)

        # Average similarity
        return (decl_sim + calls_sim + props_sim) / 3.0


class ASTParser:
    """Parse frontend code to AST using Node.js parsers"""

    def __init__(self):
        self.setup_node_environment()

    def setup_node_environment(self):
        """Create temporary Node.js script for parsing"""
        self.parser_script = """
const babel = require('@babel/parser');
const fs = require('fs');

const code = fs.readFileSync(process.argv[2], 'utf-8');
const fileType = process.argv[3];

let ast;
try {
    if (fileType === 'jsx' || fileType === 'tsx') {
        ast = babel.parse(code, {
            sourceType: 'module',
            plugins: ['jsx', 'typescript']
        });
    } else if (fileType === 'vue') {
        const compiler = require('@vue/compiler-dom');
        ast = compiler.parse(code);
    } else if (fileType === 'html') {
        const parse5 = require('parse5');
        ast = parse5.parse(code);
    } else if (fileType === 'angular') {
        // Angular uses TypeScript + template
        ast = babel.parse(code, {
            sourceType: 'module',
            plugins: ['typescript', 'decorators-legacy']
        });
    }
// 定义一个 replacer 函数来过滤循环引用
const replacer = (key, value) => {
    // 过滤掉指向父节点和文档对象的属性，这些是导致循环引用的根源
    if (key === 'parentNode' || key === 'ownerDocument') {
        return undefined;
    }
    return value;
};

// 使用 replacer 进行序列化
console.log(JSON.stringify(ast, replacer, 2));
} catch (error) {
    console.error(JSON.stringify({error: error.message}));
    process.exit(1);
}
"""

    def parse(self, code: str, file_type: str) -> Dict:
        """
        Parse code to AST

        Args:
            code: Source code string
            file_type: One of 'jsx', 'vue', 'html', 'angular'

        Returns:
            AST dictionary
        """
        # Create temporary files
        tmpdir = tempfile.mkdtemp(dir='./tmp')
        code_file = os.path.join(tmpdir, f'code.{file_type}')
        parser_file = os.path.join(tmpdir, 'parser.js')

        # Write files
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(code)
        with open(parser_file, 'w', encoding='utf-8') as f:
            f.write(self.parser_script)

        # Install dependencies (if needed)
        self._ensure_dependencies(tmpdir)

        # Run parser
        try:
            result = subprocess.run(
                ['/Users/whalexiao/.nvm/versions/node/v18.19.0/bin/node', parser_file, code_file, file_type],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                raise Exception(f"Parser error: {result.stderr}")

            return json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            raise Exception("Parser timeout")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON output: {result.stdout}")

    def _ensure_dependencies(self, tmpdir: str):
        """Ensure Node.js dependencies are installed"""
        package_json = {
            "dependencies": {
                "@babel/parser": "^7.23.0",
                "@vue/compiler-dom": "^3.3.0",
                "parse5": "^7.1.2"
            }
        }

        package_file = os.path.join(tmpdir, 'package.json')
        with open(package_file, 'w') as f:
            json.dump(package_json, f)

        # Check if already installed globally or locally
        # In production, you'd install these once
        pass


class TreeEditDistance:
    """Calculate tree edit distance using Zhang-Shasha algorithm"""

    @staticmethod
    def calculate(tree1: ASTNode, tree2: ASTNode) -> int:
        """
        Calculate tree edit distance between two AST trees

        Returns:
            Minimum number of operations to transform tree1 to tree2
        """
        # Simplified implementation - in production use zss library
        # pip install zss
        try:
            from zss import simple_distance, Node as ZSSNode

            def ast_to_zss(node: ASTNode) -> ZSSNode:
                label = f"{node.type}:{node.value}"
                zss_node = ZSSNode(label)
                for child in node.children:
                    zss_node.addkid(ast_to_zss(child))
                return zss_node

            zss_tree1 = ast_to_zss(tree1)
            zss_tree2 = ast_to_zss(tree2)

            return simple_distance(zss_tree1, zss_tree2)
        except ImportError:
            # Fallback: simple node count difference
            return abs(TreeEditDistance._count_nodes(tree1) -
                       TreeEditDistance._count_nodes(tree2))

    @staticmethod
    def _count_nodes(node: ASTNode) -> int:
        """Count total nodes in tree"""
        count = 1
        for child in node.children:
            count += TreeEditDistance._count_nodes(child)
        return count


class ASTDiffer:
    """Extract edit operations between two ASTs"""

    @staticmethod
    def extract_operations(before_ast: Dict, after_ast: Dict) -> List[Dict]:
        """
        Extract edit operations from AST diff

        Returns:
            List of operations: [{'type': 'insert|delete|update', 'node': ...}, ...]
        """
        operations = []
        ASTDiffer._diff_nodes(before_ast, after_ast, operations, [])
        return operations

    @staticmethod
    def _is_hashable(obj):
        """Check if an object is hashable"""
        try:
            hash(obj)
            return True
        except TypeError:
            return False

    @staticmethod
    def _diff_nodes(node1: Any, node2: Any, ops: List, path: List):
        """Recursively diff AST nodes"""
        if node1 is None and node2 is None:
            return

        if node1 is None:
            ops.append({'type': 'insert', 'path': path.copy(), 'node': str(node2)[:100]})
            return

        if node2 is None:
            ops.append({'type': 'delete', 'path': path.copy(), 'node': str(node1)[:100]})
            return

        # Handle dict nodes
        if isinstance(node1, dict) and isinstance(node2, dict):
            if node1.get('type') != node2.get('type'):
                ops.append({'type': 'update', 'path': path.copy(),
                            'from': node1.get('type'), 'to': node2.get('type')})

            # Check attributes
            keys = set(node1.keys()) | set(node2.keys())
            for key in keys:
                if key in ['loc', 'start', 'end', 'range', 'tokens', 'comments']:
                    continue  # Skip position info and metadata

                ASTDiffer._diff_nodes(
                    node1.get(key),
                    node2.get(key),
                    ops,
                    path + [key]
                )

        # Handle list nodes
        elif isinstance(node1, list) and isinstance(node2, list):
            # Check if all elements are hashable (simple types)
            try:
                all_hashable = (len(node1) == 0 or all(ASTDiffer._is_hashable(item) for item in node1)) and \
                               (len(node2) == 0 or all(ASTDiffer._is_hashable(item) for item in node2))
            except:
                all_hashable = False

            if all_hashable and len(node1) > 0 and len(node2) > 0:
                # Use SequenceMatcher for hashable items
                try:
                    matcher = difflib.SequenceMatcher(None, node1, node2)
                    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                        if tag == 'delete':
                            for i in range(i1, i2):
                                ops.append({'type': 'delete', 'path': path + [i],
                                            'node': str(node1[i])[:100]})
                        elif tag == 'insert':
                            for j in range(j1, j2):
                                ops.append({'type': 'insert', 'path': path + [j],
                                            'node': str(node2[j])[:100]})
                        elif tag == 'replace':
                            for i, j in zip(range(i1, i2), range(j1, j2)):
                                ASTDiffer._diff_nodes(node1[i], node2[j], ops, path + [i])
                except TypeError:
                    # Fallback if SequenceMatcher still fails
                    all_hashable = False

            if not all_hashable:
                # For unhashable items (dicts, nested lists), use index-based comparison
                max_len = max(len(node1), len(node2))
                for i in range(max_len):
                    if i >= len(node1):
                        # Insert operation
                        ops.append({'type': 'insert', 'path': path + [i],
                                    'node': str(node2[i])[:100]})
                    elif i >= len(node2):
                        # Delete operation
                        ops.append({'type': 'delete', 'path': path + [i],
                                    'node': str(node1[i])[:100]})
                    else:
                        # Recursively compare elements at same index
                        ASTDiffer._diff_nodes(node1[i], node2[i], ops, path + [i])

        # Handle primitive type differences
        elif node1 != node2:
            ops.append({'type': 'update', 'path': path.copy(),
                        'from': str(node1)[:50], 'to': str(node2)[:50]})


class ASTEditSimilarity:
    """Main class for calculating AST Edit Similarity"""

    def __init__(self, use_lightweight_parser: bool = True):
        """
        Args:
            use_lightweight_parser: If True, use simplified parsing (no Node.js needed)
        """
        self.use_lightweight = use_lightweight_parser
        if not use_lightweight_parser:
            self.parser = ASTParser()

    def calculate(
            self,
            before_code: str,
            gt_code: str,
            pred_code: str,
            file_type: str
    ) -> Dict[str, float]:
        """
        Calculate AST Edit Similarity

        Args:
            before_code: Original code before editing
            gt_code: Ground truth edited code
            pred_code: Model predicted edited code
            file_type: One of 'jsx', 'vue', 'html', 'angular'

        Returns:
            Dictionary with similarity scores:
            {
                'ast_ted': float,      # Tree edit distance based similarity
                'ast_op': float,       # Operation matching similarity
                'ast_es': float        # Combined AST Edit Similarity
            }
        """
        try:
            if self.use_lightweight:
                # Lightweight parsing (line-based approximation)
                return self._lightweight_similarity(before_code, gt_code, pred_code)
            else:
                # Full AST parsing
                return self._full_ast_similarity(before_code, gt_code, pred_code, file_type)
        except Exception as e:
            print(f"Error calculating AST similarity: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to simple line diff
            # return self._lightweight_similarity(before_code, gt_code, pred_code)

            return {
                'ast_ted': 0,
                'ast_op': 0,
                'matched_ops': 0,
                'total_gt_ops': 0,
                'total_pred_ops': 0,
                'bleu': 0,
                'bleu-4':0,
                'codebleu': 0,
                'ngram_match': 0,
                'syntax_match': 0,
                'dataflow_match': 0,
                'ast_mcs': 0,
                'ast_es':0
            }

    def _full_ast_similarity(
            self,
            before_code: str,
            gt_code: str,
            pred_code: str,
            file_type: str
    ) -> Dict[str, float]:
        """Full AST-based similarity (requires Node.js)"""
        # Parse all versions
        print("Parsing before_code...")
        before_ast = self.parser.parse(before_code, file_type)
        print("Parsing gt_code...")
        gt_ast = self.parser.parse(gt_code, file_type)
        print("Parsing pred_code...")
        pred_ast = self.parser.parse(pred_code, file_type)

        # Extract operations
        print("Extracting GT operations...")
        gt_ops = ASTDiffer.extract_operations(before_ast, gt_ast)
        print(f"Found {len(gt_ops)} GT operations")

        print("Extracting pred operations...")
        pred_ops = ASTDiffer.extract_operations(before_ast, pred_ast)
        print(f"Found {len(pred_ops)} pred operations")

        # Match operations (find common edit locations)
        print("Matching operations...")
        matched_pairs = self._match_operations(gt_ops, pred_ops)
        print(f"Matched {len(matched_pairs)} operation pairs")

        # Calculate operation similarity (where the edits are)
        ast_op = len(matched_pairs) / max(len(gt_ops), len(pred_ops)) if (gt_ops or pred_ops) else 1.0

        # Extract code content from MATCHED operations only
        gt_matched_content = ' '.join([self._extract_op_content(op1) for op1, _ in matched_pairs])
        pred_matched_content = ' '.join([self._extract_op_content(op2) for _, op2 in matched_pairs])

        print(f"GT matched content length: {len(gt_matched_content)}")
        print(f"Pred matched content length: {len(pred_matched_content)}")

        # Calculate BLEU score on matched content only
        if gt_matched_content and pred_matched_content:
            print("Calculating BLEU on matched operations...")
            bleu_results = CodeBLEUCalculator.compute_bleu(gt_matched_content, pred_matched_content)

            print("Calculating CodeBLEU on matched operations...")
            codebleu_results = CodeBLEUCalculator.compute_codebleu(
                gt_matched_content, pred_matched_content,
                gt_ast, pred_ast
            )
        else:
            print("No matched content found, using fallback scores")
            if len(pred_ops) == 0 and len(gt_ops) == 0:
                bleu_results = {'bleu': 1.0, 'bleu-1': 1.0, 'bleu-2': 1.0, 'bleu-3': 1.0, 'bleu-4': 1.0, 'bp': 1.0}
                codebleu_results = {
                    'codebleu': 1.0,
                    'ngram_match': 1.0,
                    'weighted_ngram_match': 1.0,
                    'syntax_match': 1.0,
                    'dataflow_match': 1.0
                }
            else:
                bleu_results = {'bleu': 0.0, 'bleu-1': 0.0, 'bleu-2': 0.0, 'bleu-3': 0.0, 'bleu-4': 0.0, 'bp': 0.0}
                codebleu_results = {
                    'codebleu': 0.0,
                    'ngram_match': 0.0,
                    'weighted_ngram_match': 0.0,
                    'syntax_match': 0.0,
                    'dataflow_match': 0.0
                }

        # Use CodeBLEU on matched content as modified content similarity
        ast_mcs = codebleu_results['codebleu']

        # Calculate tree edit distance similarity
        ast_ted = self._ted_similarity(gt_ast, pred_ast)

        # Combined score with CodeBLEU on matched operations
        ast_es = 0.35 * ast_ted + 0.30 * ast_op + 0.35 * ast_mcs

        return {
            'ast_ted': round(ast_ted, 4),
            'ast_op': round(ast_op, 4),
            'ast_mcs': round(ast_mcs, 4),
            'matched_ops': len(matched_pairs),
            'total_gt_ops': len(gt_ops),
            'total_pred_ops': len(pred_ops),
            'bleu': bleu_results['bleu'],
            'bleu-4': bleu_results['bleu-4'],
            'codebleu': codebleu_results['codebleu'],
            'ngram_match': codebleu_results['ngram_match'],
            'syntax_match': codebleu_results['syntax_match'],
            'dataflow_match': codebleu_results['dataflow_match'],
            'ast_es': round(ast_es, 4)
        }

    def _extract_modified_code(self, before: str, after: str) -> str:
        """
        Extract only the modified parts of code for BLEU calculation
        """
        before_lines = before.strip().split('\n')
        after_lines = after.strip().split('\n')

        differ = difflib.Differ()
        diff = list(differ.compare(before_lines, after_lines))

        modified_parts = []
        for line in diff:
            if line.startswith('+ '):
                # Added line
                modified_parts.append(line[2:])
            elif line.startswith('- '):
                # Removed line (include for context)
                modified_parts.append(line[2:])
            elif line.startswith('? '):
                # Line showing differences (skip)
                continue

        return '\n'.join(modified_parts) if modified_parts else after

    def _lightweight_similarity(
            self,
            before_code: str,
            gt_code: str,
            pred_code: str
    ) -> Dict[str, float]:
        """
        Lightweight similarity based on token/line diffing
        No external dependencies required
        """
        # Extract modified code segments
        gt_modified = self._extract_modified_code(before_code, gt_code)
        pred_modified = self._extract_modified_code(before_code, pred_code)

        # Calculate BLEU score on modified parts
        bleu_results = CodeBLEUCalculator.compute_bleu(gt_modified, pred_modified)

        # Calculate CodeBLEU (without AST since we're in lightweight mode)
        codebleu_results = CodeBLEUCalculator.compute_codebleu(
            gt_modified, pred_modified,
            reference_ast=None,
            hypothesis_ast=None
        )

        # Tokenize code
        gt_tokens = self._tokenize(before_code, gt_code)
        pred_tokens = self._tokenize(before_code, pred_code)

        # Calculate token-level edit operations
        gt_ops_set = set(gt_tokens['added'] + gt_tokens['removed'] + gt_tokens['modified'])
        pred_ops_set = set(pred_tokens['added'] + pred_tokens['removed'] + pred_tokens['modified'])

        if not gt_ops_set and not pred_ops_set:
            return {
                'ast_ted': 1.0,
                'ast_op': 1.0,
                'ast_mcs': 1.0,
                'bleu': 1.0,
                'bleu-4': 1.0,
                'codebleu': 1.0,
                'ngram_match': 1.0,
                'syntax_match': 1.0,
                'dataflow_match': 1.0,
                'ast_es': 1.0
            }

        # Operation similarity (Jaccard) - where the changes are
        intersection = len(gt_ops_set & pred_ops_set)
        union = len(gt_ops_set | pred_ops_set)
        ast_op = intersection / union if union > 0 else 0.0

        # Use CodeBLEU as modified content similarity
        ast_mcs = codebleu_results['codebleu']

        # Structure similarity (sequence matching)
        gt_lines = gt_code.strip().split('\n')
        pred_lines = pred_code.strip().split('\n')
        matcher = difflib.SequenceMatcher(None, gt_lines, pred_lines)
        ast_ted = matcher.ratio()

        # Combined
        ast_es = 0.35 * ast_ted + 0.30 * ast_op + 0.35 * ast_mcs

        return {
            'ast_ted': round(ast_ted, 4),
            'ast_op': round(ast_op, 4),
            'ast_mcs': round(ast_mcs, 4),
            'bleu': bleu_results['bleu'],
            'bleu-4': bleu_results['bleu-4'],
            'codebleu': codebleu_results['codebleu'],
            'ngram_match': codebleu_results['ngram_match'],
            'syntax_match': codebleu_results['syntax_match'],
            'dataflow_match': codebleu_results['dataflow_match'],
            'ast_es': round(ast_es, 4)
        }

    def _lightweight_content_similarity(self, gt_tokens: Dict, pred_tokens: Dict) -> float:
        """
        Calculate content similarity for lightweight mode
        Compares the actual content of added/modified lines
        """
        # Extract actual changed content
        gt_content = set(gt_tokens['added'] + [m.split(' -> ')[1] for m in gt_tokens['modified']])
        pred_content = set(pred_tokens['added'] + [m.split(' -> ')[1] for m in pred_tokens['modified']])

        # Token-level comparison
        gt_all_tokens = set()
        for line in gt_content:
            gt_all_tokens.update(line.split())

        pred_all_tokens = set()
        for line in pred_content:
            pred_all_tokens.update(line.split())

        if not gt_all_tokens and not pred_all_tokens:
            return 1.0

        intersection = len(gt_all_tokens & pred_all_tokens)
        union = len(gt_all_tokens | pred_all_tokens)

        return intersection / union if union > 0 else 0.0

    def _tokenize(self, before: str, after: str) -> Dict[str, List[str]]:
        """Extract added/removed/modified tokens"""
        before_lines = before.strip().split('\n')
        after_lines = after.strip().split('\n')

        differ = difflib.Differ()
        diff = list(differ.compare(before_lines, after_lines))

        added = [line[2:] for line in diff if line.startswith('+ ')]
        removed = [line[2:] for line in diff if line.startswith('- ')]
        modified = []

        # Detect modifications (removed + added pairs)
        i = 0
        while i < len(diff):
            if i < len(diff) - 1:
                if diff[i].startswith('- ') and diff[i + 1].startswith('+ '):
                    modified.append(f"{diff[i][2:]} -> {diff[i + 1][2:]}")
                    i += 2
                    continue
            i += 1

        return {'added': added, 'removed': removed, 'modified': modified}

    def _operation_similarity(self, ops1: List[Dict], ops2: List[Dict]) -> float:
        """Calculate similarity between two operation lists"""
        if not ops1 and not ops2:
            return 1.0

        # Convert operations to comparable format
        ops1_set = set(self._op_to_string(op) for op in ops1)
        ops2_set = set(self._op_to_string(op) for op in ops2)

        intersection = len(ops1_set & ops2_set)
        union = len(ops1_set | ops2_set)

        return intersection / union if union > 0 else 0.0

    def _match_operations(self, ops1: List[Dict], ops2: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Find matching operations between two operation lists
        Returns matched operation pairs
        """
        matched_pairs = []

        # Create operation signature for matching
        def op_signature(op):
            """Create a signature for matching operations"""
            op_type = op.get('type')
            path = op.get('path', [])
            # Use first 3 levels of path for matching (more flexible)
            path_key = '.'.join(map(str, path[:3]))
            return f"{op_type}:{path_key}"

        # Build index for ops2
        ops2_index = {}
        for i, op in enumerate(ops2):
            sig = op_signature(op)
            if sig not in ops2_index:
                ops2_index[sig] = []
            ops2_index[sig].append((i, op))

        # Match ops1 with ops2
        used_indices = set()
        for op1 in ops1:
            sig = op_signature(op1)
            if sig in ops2_index:
                # Find first unused match
                for idx, op2 in ops2_index[sig]:
                    if idx not in used_indices:
                        matched_pairs.append((op1, op2))
                        used_indices.add(idx)
                        break

        return matched_pairs

    def _modified_content_similarity(self, ops1: List[Dict], ops2: List[Dict]) -> float:
        """
        Calculate similarity of modified content (what was changed to)
        Only considers matched operations (same edit locations)
        """
        if not ops1 and not ops2:
            return 1.0

        # Find matched operations
        matched_pairs = self._match_operations(ops1, ops2)

        if not matched_pairs:
            return 0.0

        # Extract content from matched operations only
        gt_content = []
        pred_content = []

        for op1, op2 in matched_pairs:
            # Extract content from GT operation
            gt_text = self._extract_op_content(op1)
            if gt_text:
                gt_content.append(gt_text)

            # Extract content from pred operation
            pred_text = self._extract_op_content(op2)
            if pred_text:
                pred_content.append(pred_text)

        if not gt_content and not pred_content:
            return 1.0

        # Join content for comparison
        gt_code = ' '.join(gt_content)
        pred_code = ' '.join(pred_content)

        # Method 1: Token-level similarity
        token_sim = self._token_similarity(gt_content, pred_content)

        # Method 2: BLEU score on matched content
        bleu_result = CodeBLEUCalculator.compute_bleu(gt_code, pred_code)
        bleu_sim = bleu_result['bleu']

        # Method 3: Semantic similarity (operation types and values)
        semantic_sim = self._semantic_operation_similarity_matched(matched_pairs)

        # Weighted combination
        mcs = 0.35 * token_sim + 0.40 * bleu_sim + 0.25 * semantic_sim

        return mcs

    def _extract_op_content(self, op: Dict) -> str:
        """Extract content text from an operation"""
        op_type = op.get('type')

        if op_type == 'insert':
            return str(op.get('node', ''))
        elif op_type == 'update':
            return f"{op.get('from', '')} {op.get('to', '')}"
        elif op_type == 'delete':
            return str(op.get('node', ''))

        return ''

    def _semantic_operation_similarity_matched(self, matched_pairs: List[Tuple[Dict, Dict]]) -> float:
        """
        Calculate semantic similarity for matched operation pairs
        """
        if not matched_pairs:
            return 0.0

        total_score = 0.0

        for op1, op2 in matched_pairs:
            # Same operation type at same location is guaranteed by matching
            # Now check content similarity

            content1 = self._extract_op_content(op1)
            content2 = self._extract_op_content(op2)

            if not content1 and not content2:
                total_score += 1.0
                continue

            # Token overlap
            tokens1 = set(content1.split())
            tokens2 = set(content2.split())

            if tokens1 or tokens2:
                overlap = len(tokens1 & tokens2)
                union = len(tokens1 | tokens2)
                total_score += overlap / union if union > 0 else 0.0
            else:
                total_score += 1.0

        return total_score / len(matched_pairs)

    def _extract_operation_content(self, ops: List[Dict]) -> List[str]:
        """Extract actual content changes from operations"""
        content = []
        for op in ops:
            op_type = op.get('type')
            if op_type == 'insert':
                content.append(str(op.get('node', '')))
            elif op_type == 'update':
                content.append(f"{op.get('from', '')}->{op.get('to', '')}")
            elif op_type == 'delete':
                content.append(f"DEL:{op.get('node', '')}")
        return content

    def _token_similarity(self, content1: List[str], content2: List[str]) -> float:
        """Calculate token-level similarity between modified contents"""
        if not content1 and not content2:
            return 1.0

        # Flatten and tokenize
        tokens1 = set(' '.join(content1).split())
        tokens2 = set(' '.join(content2).split())

        if not tokens1 and not tokens2:
            return 1.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0

    def _semantic_operation_similarity(self, ops1: List[Dict], ops2: List[Dict]) -> float:
        """
        Calculate semantic similarity of operations
        Considers operation type, target attributes, and value changes
        """
        if not ops1 and not ops2:
            return 1.0

        # Group operations by type and path
        def group_ops(ops):
            groups = {}
            for op in ops:
                key = f"{op['type']}:{'.'.join(map(str, op.get('path', [])[:3]))}"  # Use first 3 levels
                if key not in groups:
                    groups[key] = []
                groups[key].append(op)
            return groups

        groups1 = group_ops(ops1)
        groups2 = group_ops(ops2)

        # Calculate group overlap
        all_keys = set(groups1.keys()) | set(groups2.keys())
        if not all_keys:
            return 0.0

        matching_score = 0.0
        for key in all_keys:
            if key in groups1 and key in groups2:
                # Same operation type at similar path - high score
                matching_score += 1.0
            elif key in groups1 or key in groups2:
                # Only in one set - check for similar operations
                ops_in_1 = groups1.get(key, [])
                ops_in_2 = groups2.get(key, [])
                # Partial credit for related operations
                matching_score += 0.3

        return matching_score / len(all_keys) if all_keys else 0.0

    def _structural_operation_similarity(self, ops1: List[Dict], ops2: List[Dict]) -> float:
        """
        Calculate structural similarity considering operation depth and order
        """
        if not ops1 and not ops2:
            return 1.0

        # Extract path depths and operation patterns
        def get_patterns(ops):
            patterns = []
            for op in ops:
                path = op.get('path', [])
                depth = len(path)
                patterns.append(f"{op['type']}@{depth}")
            return patterns

        patterns1 = get_patterns(ops1)
        patterns2 = get_patterns(ops2)

        # Use sequence matching to consider order
        matcher = difflib.SequenceMatcher(None, patterns1, patterns2)
        return matcher.ratio()

    def _op_to_string(self, op: Dict) -> str:
        """Convert operation to comparable string"""
        return f"{op['type']}:{'.'.join(map(str, op.get('path', [])))}"

    def _ted_similarity(self, ast1: Dict, ast2: Dict) -> float:
        """Calculate tree edit distance based similarity"""
        # Simplified: count matching nodes
        nodes1 = self._count_node_types(ast1)
        nodes2 = self._count_node_types(ast2)

        all_types = set(nodes1.keys()) | set(nodes2.keys())
        total_diff = sum(abs(nodes1.get(t, 0) - nodes2.get(t, 0)) for t in all_types)
        total_nodes = sum(nodes1.values()) + sum(nodes2.values())

        return 1 - (total_diff / total_nodes) if total_nodes > 0 else 0.0

    def _count_node_types(self, ast: Any, counts: Dict = None) -> Dict[str, int]:
        """Count occurrences of each node type"""
        if counts is None:
            counts = {}

        if isinstance(ast, dict):
            node_type = ast.get('type', 'unknown')
            counts[node_type] = counts.get(node_type, 0) + 1

            for value in ast.values():
                self._count_node_types(value, counts)

        elif isinstance(ast, list):
            for item in ast:
                self._count_node_types(item, counts)

        return counts


# Example usage
def example_usage():
    """Example of how to use the AST Edit Similarity calculator"""

    before_code = """
function Button() {
  return <button className="bg-blue-500">Click me</button>;
}
"""

    gt_code = """
function Button() {
  return <button className="bg-red-500 text-white">Click me</button>;
}
"""

    pred_code = """
function Button() {
  return <button className="bg-red-600 text-white font-bold">Click me</button>;
}
"""

    # Using lightweight parser (no dependencies)
    calculator = ASTEditSimilarity(use_lightweight_parser=False)

    results = calculator.calculate(
        before_code=before_code,
        gt_code=gt_code,
        pred_code=pred_code,
        file_type='jsx'
    )

    print("AST Edit Similarity Results:")
    print(f"  AST-TED (Tree Edit Distance):  {results['ast_ted']:.4f}")
    print(f"  AST-OP (Operation Matching):   {results['ast_op']:.4f}")
    print(f"  AST-ES (Combined):             {results['ast_es']:.4f}")

    return results


def ast_code_similarity(src_code, reference_code, generated_code, framework):
    """
    Calculate AST-based code similarity between reference and generated edits
    CodeBLEU is computed only on matched edit locations (AST-OP matches)

    Args:
        src_code: Original source code
        reference_code: Ground truth edited code
        generated_code: Model-generated edited code

    Returns:
        dict: Dictionary containing all similarity metrics
    """
    # Using full AST parser
    calculator = ASTEditSimilarity(use_lightweight_parser=False)

    framework_filetype_dic = {
        "vue": "vue",
        "react": "jsx",
        "vanilla": "html",
        "angular": "angular"

    }

    results = calculator.calculate(
        before_code=src_code,
        gt_code=reference_code,
        pred_code=generated_code,
        file_type=framework_filetype_dic[framework]
    )

    print("\n" + "=" * 70)
    print("AST Edit Similarity Results (CodeBLEU on Matched Operations)")
    print("=" * 70)
    print(f"  AST-TED (Tree Edit Distance):     {results['ast_ted']:.4f}")
    print(f"  AST-OP (Operation Matching):      {results['ast_op']:.4f}")
    print(f"    - Matched operations:            {results['matched_ops']}")
    print(f"    - Total GT operations:           {results['total_gt_ops']}")
    print(f"    - Total Pred operations:         {results['total_pred_ops']}")
    print("-" * 70)
    print("BLEU Scores (on matched operations only):")
    print(f"  BLEU:                             {results['bleu']:.4f}")
    print(f"  BLEU-4:                           {results['bleu-4']:.4f}")
    print("-" * 70)
    print("CodeBLEU Components (on matched operations only):")
    print(f"  CodeBLEU:                         {results['codebleu']:.4f}")
    print(f"  N-gram Match:                     {results['ngram_match']:.4f}")
    print(f"  Syntax Match:                     {results['syntax_match']:.4f}")
    print(f"  Dataflow Match:                   {results['dataflow_match']:.4f}")
    print("-" * 70)
    print(f"  AST-MCS (Modified Content):       {results['ast_mcs']:.4f}")
    print(f"  AST-ES (Combined Score):          {results['ast_es']:.4f}")
    print("=" * 70 + "\n")

    # return results
    return results['ast_op'], results['ast_mcs']



def compute_edit_bleu(src_code, reference_code, generated_code):
    """
    Compute BLEU score specifically for the edited portions

    Args:
        src_code: Original source code
        reference_code: Ground truth edited code
        generated_code: Model-generated edited code

    Returns:
        dict: BLEU scores
    """
    calculator = ASTEditSimilarity(use_lightweight_parser=True)

    # Extract modified parts
    gt_modified = calculator._extract_modified_code(src_code, reference_code)
    pred_modified = calculator._extract_modified_code(src_code, generated_code)

    # Calculate BLEU
    bleu_results = CodeBLEUCalculator.compute_bleu(gt_modified, pred_modified)

    print("\n" + "=" * 60)
    print("BLEU Scores on Modified Code:")
    print("=" * 60)
    print(f"  BLEU:      {bleu_results['bleu']:.4f}")
    print(f"  BLEU-1:    {bleu_results['bleu-1']:.4f}")
    print(f"  BLEU-2:    {bleu_results['bleu-2']:.4f}")
    print(f"  BLEU-3:    {bleu_results['bleu-3']:.4f}")
    print(f"  BLEU-4:    {bleu_results['bleu-4']:.4f}")
    print(f"  BP:        {bleu_results['bp']:.4f}")
    print("=" * 60 + "\n")

    return bleu_results


def compute_edit_codebleu(src_code, reference_code, generated_code):
    """
    Compute CodeBLEU score specifically for the edited portions

    Args:
        src_code: Original source code
        reference_code: Ground truth edited code
        generated_code: Model-generated edited code

    Returns:
        dict: CodeBLEU scores
    """
    calculator = ASTEditSimilarity(use_lightweight_parser=False)

    # Extract modified parts
    gt_modified = calculator._extract_modified_code(src_code, reference_code)
    pred_modified = calculator._extract_modified_code(src_code, generated_code)

    # Parse ASTs
    gt_ast = calculator.parser.parse(reference_code, 'jsx')
    pred_ast = calculator.parser.parse(generated_code, 'jsx')

    # Calculate CodeBLEU
    codebleu_results = CodeBLEUCalculator.compute_codebleu(
        gt_modified, pred_modified,
        gt_ast, pred_ast
    )

    print("\n" + "=" * 60)
    print("CodeBLEU Scores on Modified Code:")
    print("=" * 60)
    print(f"  CodeBLEU:          {codebleu_results['codebleu']:.4f}")
    print(f"  N-gram Match:      {codebleu_results['ngram_match']:.4f}")
    print(f"  Weighted N-gram:   {codebleu_results['weighted_ngram_match']:.4f}")
    print(f"  Syntax Match:      {codebleu_results['syntax_match']:.4f}")
    print(f"  Dataflow Match:    {codebleu_results['dataflow_match']:.4f}")
    print("=" * 60 + "\n")

    return codebleu_results


if __name__ == "__main__":
    # Example 1: Basic usage
    print("Example 1: Basic AST Similarity")
    example_usage()
#
#     # Example 2: BLEU on edits
#     print("\n" + "=" * 60)
#     print("Example 2: BLEU Score on Modified Code")
#     print("=" * 60)
#
#     before = """
# function Button() {
#   return <button className="bg-blue-500">Click me</button>;
# }
# """
#
#     gt = """
# function Button() {
#   return <button className="bg-red-500 text-white">Click me</button>;
# }
# """
#
#     pred = """
# function Button() {
#   return <button className="bg-red-600 text-white font-bold">Click me</button>;
# }
# """
#
#     bleu_scores = compute_edit_bleu(before, gt, pred)
#
#     # Example 3: CodeBLEU on edits
#     print("\n" + "=" * 60)
#     print("Example 3: CodeBLEU Score on Modified Code")
#     print("=" * 60)
#
#     # codebleu_scores = compute_edit_codebleu(before, gt, pred)
#
#     # Example 4: Full comparison
#     print("\n" + "=" * 60)
#     print("Example 4: Complete Analysis")
#     print("=" * 60)
#
#     full_results = ast_code_similarity(before, gt, pred)