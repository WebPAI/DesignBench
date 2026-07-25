import json
import numpy as np
from PIL import Image
import pandas as pd


def get_compile_error(file_name):
    # with open(f"results/res_vanilla_react.json", "r") as fs:
    with open(file_name, "r") as fs:
        data = json.loads(fs.read())

    res = {}
    for model in data.keys():
        res[model] = {}
        for web_name in data[model].keys():
            # difficulty = get_difficulty(src_frame, web_name)
            if "compile_error" in data[model][web_name] and data[model][web_name]["compile_error"] != "NULL":
                error_type = data[model][web_name]["compile_error"]
                if error_type == "blank":
                    continue
                error_type = map_error(error_type)
                if error_type in res[model]:
                    res[model][error_type] += 1
                else:
                    res[model][error_type] = 1
                # print(error_type)

    print(json.dumps(res, indent=4))
    return res


def map_error(error_message):
    # Angular

    if "Incomplete block" in error_message:
        return "Incomplete Block"

    if "Invalid ICU message" in error_message:
        return "Invalid ICU Message"

    if "Unable to parse entity" in error_message:
        return "Unable to Parse Entity"

    if "Cannot find module" in error_message:
        return "Component Import Error"
    if "Property 'ngOnInit' is missing" in error_message:
        # return "Property 'ngOnInit' Missing"
        return "Property Error"
    if "2306" in error_message:
        # return "x File is not a module"
        return "Component Import Error"
    if "Unexpected closing tag" in error_message:
        return "Unexpected Closing Tag"
    if "Unexpected closing block" in error_message:
        return "Unexpected Closing Block"
    if "Opening tag" in error_message:
        # return "Opening Tag"
        return "Tag Error"
    if "Unexpected character" in error_message:
        # return "Unexpected Character"
        return "Unexpected Token"

    if "is a Web Component then add 'CUSTOM_ELEMENTS_SCHEMA' to" in error_message:
        # return "IF 'xxx' is a Web Component then add 'CUSTOM_ELEMENTS_SCHEMA' to the '@Component.schemas'"
        return "Component Define Error"

    if "Only void, custom and foreign elements can be self closed" in error_message:
        # return "Only void, custom and foreign elements can be self closed"
        # return "Element Tag Error"
        return "Tag Error"

    if "Value could not be determined statically" in error_message:
        # return "Value could not be determined statically"
        # return "Value could not be determined statically"
        return "Component Import Error"

    if "Void elements do not have end tags" in error_message:
        # return "Void elements do not have end tags"
        # return "Element Tag Error"
        return "Tag Error"

    if "Object literal may only specify known properties" in error_message:
        # return "Object literal may only specify known properties"
        return "Property Error"

    if "Component imports must be standalone components, directives, pipes, or must be NgModules" in error_message:
        # return "Component imports must be standalone components, directives, pipes, or must be NgModules"
        return "Component Import Error"

    if "Module '\"./new.component\"' has no exported member" in error_message:
        # return "Module has no exported member"
        return "Component Export Error"
    if "Module '\"./new.component\"' declares 'NewComponent' locally, but it is not exported" in error_message:
        # return "Module declares locally, but it is not exported"
        return "Component Export Error"

    if "The `*ngIf` directive was used in the template, but neither the `NgIf` directive nor the `CommonModule` was imported" in error_message:
        # return "The `*ngIf` directive was used in the template, but neither the `NgIf` directive nor the `CommonModule` was imported"
        return "Component Import Error"

    if "TS1005: ',' expected." in error_message:
        # return ", expected"
        return "Unexpected Token"

    if "NG9" in error_message:
        return "Property Error"
        # return "Property Does Not Exist on Type"

    if "NG8003" in error_message:
        return "Missing Reference Target"

    if "NG8002" in error_message:
        return "Binding Errors"

        # return "Can't bind to, since it isn't a known property of"

    ### React
    # if "Unexpected token" in error_message:
    #     return "Unexpected token"
    # if "Unterminated string constant" in error_message:
    #     return "Unterminated string constant"
    # if "defined multiple times" in error_message:
    #     return "defined multiple times"
    # if "Expression expected" in error_message:
    #     return "Expression expected"
    # if "Unexpected eof" in error_message:
    #     return "Unexpected eof"
    # if "Identifier cannot follow number" in error_message:
    #     return "Identifier cannot follow number"
    # if "You're importing a component that needs useState." in error_message:
    #     return "use client missing"
    # if "'import', and 'export' cannot be used outside of module code" in error_message:
    #     return "'import', and 'export' cannot be used outside of module code"
    # if "not supported in app/" in error_message:
    #     return "not supported in app/"
    #
    # if "Expected" in error_message and "got" in error_message:
    #     return "Expected x, got x."

    if "Unexpected token" in error_message:
        return "Unexpected Token"
    if "Unterminated string constant" in error_message:
        return "Unterminated String Constant"
    if "defined multiple times" in error_message:
        return "Variable Defined Multiple Times"
    if "Expression expected" in error_message:
        return "Expression Expected"
    if "Unexpected eof" in error_message:
        return "Unexpected EOF"
    if "Identifier cannot follow number" in error_message:
        return "Identifier Cannot Follow Number"
    if "You're importing a component that needs useState." in error_message:
        return "Use Client Missing"

    if "'import', and 'export' cannot be used outside of module code" in error_message:
        # return "Import or Export Error"
        return "Import Error"
        # return "'import', and 'export' cannot be used outside of module code"
    if "not supported in app/" in error_message:
        return "Function not Supported in app/"

    if "Expected" in error_message and "got" in error_message:
        # return "Expected x, got x."
        return "Unexpected Token"
    if " Expected ';', '}' or &lt;eof&gt;" in error_message:
        return "Unexpected Token"

    ### Vue

    # if "Parenthesized expression cannot be empty" in error_message:
    #     return "Parenthesized expression cannot be empty"
    #
    # if "Unexpected EOF in tag" in error_message:
    #     return "Unexpected EOF in tag"
    #
    # if "Error parsing JavaScript expression" in error_message:
    #     return "Error parsing JavaScript expression"
    # if "Failed to resolve import" in error_message:
    #     return "Failed to resolve import"
    #
    # if "At least one &lt;template" in error_message:
    #     return "No Template"
    # if "Cannot apply unknown utility class" in error_message:
    #     return "Cannot apply unknown utility class"
    # if "Single file component can contain only one" in error_message:
    #     return "Single file component can contain only one template"
    # if "Missing closing } at" in error_message:
    #     return "Missing closing }"
    # if "Attribute name cannot contain" in error_message or "Attribute name cannot start with" in error_message:
    #     return "Attribute name error"
    #
    # if "has already been declared" in error_message:
    #     return "Identifier has already been declared"
    # if "expects exactly one child element or component" in error_message:
    #     return "Transition expects exactly one child element or component"
    # if "Unquoted attribute value cannot contain" in error_message:
    #     return "Unquoted attribute value cannot contain special value"
    #
    # if "Tags with side effect" in error_message:
    #     return "Tags with side effect (<script> and <style>) are ignored in client component templates"

    if "Parenthesized expression cannot be empty" in error_message:
        return "Parenthesized expression cannot be empty"

    if "Unexpected EOF in tag" in error_message:
        return "Unexpected EOF"
    if "Element is missing end tag" in error_message:
        return "Missing End Tag"

    if "Invalid end tag." in error_message:
        return "Invalid End Tag"

    if "Unexpected '/'" in error_message:
        return "Unexpected Token"

    if "Illegal '/' in tags" in error_message:
        return "Illegal Slash"

    if "Package path ./tailwind.css is not exported" in error_message:
        return "Tailwind Export Error"

    if "Error parsing JavaScript expression" in error_message:
        return "JavaScript Expression Parsing Error"
    if "Failed to resolve import" in error_message:
        return "Import Error"

    if "At least one &lt;template" in error_message:
        # return "No Template"
        return "Template Error"
    if "Cannot apply unknown utility class" in error_message:
        return "Unknown Utility Class"
    if "Single file component can contain only one" in error_message:
        # return "Multiple Template in Single File"
        return "Template Error"
    if "Missing closing } at" in error_message:
        return "Missing Closing Brace"
    if "Attribute name cannot contain" in error_message or "Attribute name cannot start with" in error_message:
        # return "Attribute Name Error"
        return "Attribute Error"

    if "Duplicate attribute." in error_message:
        return "Duplicate Attribute"

    if "has already been declared" in error_message:
        return "Duplicate Identifier"

    if "expects exactly one child element or component" in error_message:
        return "Transition Error"
    if "Unquoted attribute value cannot contain" in error_message:
        # return "Unquoted Attribute Error"
        return "Attribute Error"

    if "Tags with side effect" in error_message:
        return "Side Effect Tags"

    if "Could not resolve value" in error_message:
        return "Could not resolve value"

    if "cannot reassign to an imported binding" in error_message:
        return "Cannot reassign to an imported binding"

    if "Unable to initialize JavaScript cache storage" in error_message:
        return "Unable to initialize JavaScript cache storage"

    if "Property 'caret' does not exist on type" in error_message:
        return "Property does not exist on type"

    if "is missing in type" in error_message:
        return "Property is missing in type"

    if "is not assignable to" in error_message:
        return "Not assignable"

    if "does not exist on type" in error_message:
        return "Property does not exist on type"

    return error_message


def get_compile(frame_work="vue"):
    # src_frames = ["angular", "react", "vue"]
    # src_frames = ["angular"]
    src_frames = [frame_work]
    # dst_frames = ["angular", "react", "vue", "vanilla"]
    dst_frames = ["vue"]

    # calculate_size_label()

    res = []

    error_counts = {}
    for src_frame in src_frames:
        for dst_frame in dst_frames:
            dst_frame = src_frame
            # print(src_frame, dst_frame)
            errors = get_compile_error(file_name=f"{res_dir}/{src_frame}_{dst_frame}.json")

            for key in errors:
                for error in errors[key]:
                    if error in error_counts:
                        error_counts[error] += errors[key][error]
                    else:
                        error_counts[error] = errors[key][error]
                errors[key] = sum(errors[key].values())
            # print(errors)
            # print(json.dumps(errors, indent=4))

    print(json.dumps(error_counts, indent=4))

    # res = []
    # for src_frame in ["angular", "react", "vue"]:
    #         # dst_frame = src_frame
    #         # print(src_frame, dst_frame)
    #     errors = get_compile_error(file_name=f"./designedit/{src_frame}_both.json")

    # res = []
    # for src_frame in ["angular", "react", "vue"]:
    #         # dst_frame = src_frame
    #         # print(src_frame, dst_frame)
    #     errors = get_compile_error(file_name=f"./designedit/{src_frame}_both.json")
    #
    #     for key in errors:
    #         errors[key] = sum(errors[key].values())
    #     print(errors)


res_dir = "../res_new/DesignGeneration"
get_compile(frame_work="react")
get_compile(frame_work="vue")
get_compile(frame_work="angular")