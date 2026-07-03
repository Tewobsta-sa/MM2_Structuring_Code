````markdown
# MM2 Codebase Style Guide

This document establishes the official formatting and style standards for all MM2 code blocks across the repository. The primary goal is to ensure absolute readability and maintainability by enforcing structural consistency over visual alignment tricks.

---

## Indentation Rules

### 1. Indentation Width

- Use **2 spaces** per indentation level consistently.
- Never use tabs.
- Each nested expression increases indentation by exactly 2 spaces.

### 2. Top-Level Forms

- Top-level expressions (`DEF`, `MACRO`, `exec`, etc.) must start at column 0.
- Body content must be indented by 2 spaces.

```mm2
(DEF fork
  (, ((fork $ctx) ($case/0)))
  (, ((join ($ctx case/0)) $case/0))
)
```
````

---

## Parentheses Rules

### 3. Closing Parentheses

- Place each closing parenthesis on its own line.
- Align closing parentheses vertically with their opening expression.
- Never place multiple closing parentheses on the same line.

```mm2
((union ($in_a $in_b) -> $out)
  (, ($in_a $a)
    ($in_b $b)
  )
  (, ($out $a)
    ($out $b)
  )
)
```

### 4. Opening Parentheses

- The opening parenthesis must stay on the same line as the first element of that expression.
- For multi-line expressions, the opening parenthesis sits at the end of the line.

---

## Spacing Rules

### 5. No Trailing Spaces for Alignment

- Do not add arbitrary spaces to align similar expressions vertically.
- Rely on consistent block indentation instead of visual alignment.

**Incorrect** (alignment-based):

```mm2
(, ($in_a $a)
  ($in_b $b)
)
```

**Correct** (indentation-based):

```mm2
(, ($in_a $a)
  ($in_b $b)
)
```

### 6. Space After Commas

- Include a single space after the `,` operator in source/sink lists.
- Do not place a space before the `,` operator.

```mm2
(, (file1 $x)
  (projected $x)
)
```

---

## Nested Expression Rules

### 7. Consistent Nesting Indentation

- Each progressive nesting level adds exactly 2 spaces relative to its parent container.
- Do not introduce arbitrary indentation jumps or cascade patterns based on upper text length.

```mm2
(exec 0 (, $x)
  (, 0
    (exec 0 (, 0)
      (, 1
        (exec 0 (, 1)
          (, 2
            (exec 0 (, 2)
              (, 3)
            )
          )
        )
      )
    )
  )
)
```

---

## MACRO / DEF Rules

### 8. MACRO Body Structure

- Pattern parameters must be placed on a separate line directly below the `MACRO` declaration.
- The macro body must be indented by 2 spaces.
- Each clause within the body must occupy its own separate line.

```mm2
(MACRO
  (join $proc $op)
  (, ($proc $op (join ($ctx case/2)) $case/2)
    ($proc $op (join ($ctx arg/0)) $x)
    ($proc $op (join ($ctx arg/1)) $y)
    ($op ($case/2 $x $y) -> $out)
  )
  (, ($proc $op (join $ctx) $out))
)
```

### 9. DEF Case Consistency

- All case definitions (e.g., `case/0`, `case/1`, `case/2`) must maintain an identical structural layout.
- Do not introduce extra spacing tricks for visual alignment between divergent cases.

```mm2
; case/0
(DEF fork
  (, ((fork $ctx) ($case/0)))
  (, ((join ($ctx case/0)) $case/0))
)
; case/1
(DEF fork
  (, ((fork $ctx) ($case/1 $x)))
  (, ((fork ($ctx arg/0)) $x)
    ((join ($ctx case/1)) $case/1)
  )
)

```

---

## Comment Rules

### 10. Comment Placement

- Comments must begin with a semicolon `;` followed by a single space.
- Place block comments directly before the block of code they describe.
- For inline comments, separate them from the code trailing edge using exactly 2 spaces.

```mm2
; case/0
(DEF fork
  (, ((fork $ctx) ($case/0)))
  (, ((join ($ctx case/0)) $case/0))
)
```

---

## Exec Rules

### 11. Exec Structure

- The priority value must remain on the same line as the `exec` statement.
- Sources and sinks must follow on separate lines, indented cleanly by 2 spaces.
- The closing parenthesis must align directly with the start of the `exec` keyword.

```mm2
(exec 0
  (, (a $x) (b $y))
  (, (ab $x $y))
)
```
