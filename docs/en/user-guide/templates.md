# Template Development

How to create custom video templates.

---

## Template Introduction

Video templates use HTML to define the layout and style of video frames.

---

## Template Structure

Templates are located in the `templates/` directory, grouped by size:

```
templates/
├── 1080x1920/  # Portrait
├── 1920x1080/  # Landscape
└── 1080x1080/  # Square
```

---

## Creating Templates

1. Copy an existing template file
2. Modify HTML and CSS
3. Save to the corresponding size directory
4. Select and use in Web interface

---

## Template Variables

Templates support the following variables:

- `{{ title }}` - Video title
- `{{ text }}` - Scene text
- `{{ image }}` - Scene image

---

## More Information

Detailed template development guide coming soon.

