# Manual Annotation Guidelines

## DesignGeneration

Task Overview

You will be given some web links with diverse topics. Your task is to classify them into several topic categories based on the contents of the websites (e.g., homepage, news, social, blog, product, etc.). Please assign each webpage a topic name that you think is most appropriate.

## DesignEdit

Task Overview

You will be provided with a webpage link or a UI design specification. Your task is to annotate each webpage or UI design with the most appropriate topic name based on the type and difficulty level of UI modifications required. The annotations should cover the operation type, the UI attribute type being adjusted, and the difficulty level of the modifications. The goal is to provide clear and consistent annotations to guide UI design and development processes.

Guidelines

1. Compile Dimension
After applying the edit, evaluate whether the UI compiles successfully:

- Yes: The modified UI compiles and renders correctly
- No: The UI fails to compile due to syntax, logic, or component structure issues

2. Instruction Clarity Dimension
Rate the clarity of the edit instruction provided in the prompt:

- Low: Vague, ambiguous, or missing critical information
- Moderate: Understandable with some assumptions or clarifications needed
- High: Clear, specific, and directly actionable

3. Operation Number
Estimate the number of distinct editing operations required to complete the modification:

- Numeric value (e.g., 1, 2, 3...)
Example: A task requiring changing color and adding paddings between elements as 2 operations.

4. Action Type Dimension

Annotate the type of action being performed on the UI elements. The action types include:

- Add: Introducing new UI elements to the webpage or design.
Examples: Adding a new button, inserting a text field, or incorporating an image.

- Change: Modifying existing UI elements without adding or removing them.
Examples: Updating text content, altering button color, or repositioning an element.

- Delete: Removing existing UI elements from the webpage or design.
Examples: Removing a sidebar, deleting a pop-up, or eliminating a redundant icon.

5. Visual Label Dimension

Annotate the specific UI attribute being adjusted. The UI attribute types include:

- Text: Modifications to content, font, or typography.
Examples: Changing button labels, adjusting font size, or updating text alignment.

- Color: Adjustments to background colors, text colors, or accent colors.
Examples: Changing the background to a darker shade, updating link colors, or modifying hover effects.

- Position: Changes to the spatial arrangement or layout of elements.
Examples: Repositioning a navigation bar, adjusting element spacing, or realigning content blocks.

- Size: Modifications to the dimensions or scaling of elements.
Examples: Resizing an image, adjusting button width, or scaling a modal window.

- Shape: Geometric or structural changes to elements.
Examples: Rounding button corners, changing an icon’s shape, or modifying a container’s border.

- Component-Level: Holistic changes affecting entire UI components.
Examples: Redesigning a header, updating a form’s structure, or modifying an entire card component.

6. Difficulty Level Dimension

Annotate the difficulty level of the UI edit. Please classify them into low/medium/high considering the following factors:

Number of Elements: The count of UI elements requiring modification.

- Low: 1–3 elements.

- Medium: 4–5 elements.

- High: 6 or more elements.

Interdependencies: The complexity of relationships between modified elements.

- Low: Modifications are independent (e.g., changing a single button’s color).

- Medium: Modifications affect related elements (e.g., repositioning a button affects adjacent elements).

- High: Modifications impact multiple components or require significant restructuring (e.g., updating a navigation bar affects the entire layout).


Cascading Changes: The scope of additional changes needed to maintain design consistency and functionality.

- Low: No or minimal cascading changes (e.g., changing text color with no impact on other elements).

- Medium: Moderate cascading changes (e.g., resizing an element requires adjusting adjacent elements).

- High: Extensive cascading changes (e.g., modifying a component requires updates across multiple sections to ensure consistency).

## DesignRepair

Task Overview

Your task is to identify and annotate UI layout issues that should be repaired. You will be provided with screenshots of webpages or UI components. For each screenshot, annotate visible layout flaws according to the following six categories. Provide clear red bounding boxes around problematic areas and assign the correct category label.

Guidelines

1. Occlusion:
UI elements are fully or partially covered by other components, making them inaccessible or invisible.
e.g., A label being blocked by a floating button or image frame.

2. Crowding:
Too many elements are squeezed into a limited area with narrowed/no padding between them, resulting in a cramped or cluttered layout.

3. Alignment:
Elements are not aligned properly relative to each other or the layout grid, creating a visually unbalanced interface.
e.g., Titles misaligned with icons or input fields out of sync.

4. Color and contrast:
Poor color contrast between foreground and background impairs readability or usability, particularly for visually impaired users.
e.g., Light gray text on a white background.

5. Overflow:
UI content spills outside its container boundaries, causing layout breakage such as unintended scrollbars or clipped text.
e.g., Long text extending beyond a button or modal box.
