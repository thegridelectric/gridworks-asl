# Codegen update: XSLT -> python, jinja


For “AI + human” readability and maintainability, we are going to migrate all of our xslt to Python + Jinja2 (or pure Python emit).  Our  codegen has a lot of cross-cutting logic (axioms, version strategies, format exceptions, imports) that’s simply easier to express, test, and evolve in Python.

###  Why move DeriveTypes to Python

* Legibility (for humans & LLMs): LLMs (and colleagues) reason far better about Python control flow than XPath/XSLT templates sprinkled with text nodes
* Debuggability: You get real stepping, logging, asserts, and exceptions. No more operator-precedence or node-set gotchas.
* Tests & goldens: Pytest + “golden file” tests for each named type; snapshot diffs are trivial to manage.

Types & CI hygiene: Pydantic/mypy for the IR, Black/Ruff for output formatting; failing fast if a field is missing (Jinja2 StrictUndefined).

Future logic: Easier to add rules (e.g., “no validator for lists of versioned subtypes unless explicit axiom”) without XPath contortions.

When to keep XSLT

Straight mapping of XML → YAML fragments where the logic is essentially structural and stable (e.g., some enum/registry materialization).

Very large XML reshapes where an existing XSLT is clean and rarely changes.

### Suggested Python architecture (concise)

- 1 **Parse to an IR** (intermediate representation):

```@dataclass(frozen=True)
class AttributeIR:
    name_py: str
    name_camel: str
    is_required: bool
    is_list: bool
    is_type: bool
    subtype_name: str | None
    subtype_has_dataclass: bool
    primitive_format: str | None
    primitive_type: str | None
    axiom: str | None

@dataclass(frozen=True)
class TypeIR:
    type_name: str
    version: str
    class_name: str
    extra_allowed: bool
    attributes: list[AttributeIR]
    multi_axioms: list[...]
```
 -2 **Rules in Python** (e.g., needs_single_prop_validator(attr)), not in the template.
 -3 **Render** with Jinja2 templates (StrictUndefined) or emit with small Python formatters
 -4 **Format & lint**: run Black/Ruff on gen files
 -5 **Golden tets** per type, 

 ### Minimal Jinja2 example
 ```
 class {{ ir.class_name }}(GwBase):
    """ASL schema of record [{{ ir.type_name }} v{{ ir.version }}](...)"""
    {% for a in ir.attributes -%}
    {{ a.name_py }}: {{ a.py_annotation }}
    {% endfor %}

    type_name: Literal["{{ ir.type_name }}"] = "{{ ir.type_name }}"
    version: Literal["{{ ir.version }}"] = "{{ ir.version }}"

    {# single-property validators #}
    {% for a in ir.attributes if needs_single_prop_validator(a) -%}
    @model_validator(mode="{{ 'before' if pre_validate(a) else 'after' }}")
    def {{ spv_name(a) }}(self) -> Self:
        {{ validator_body(a) }}
        return self
    {% endfor %}

    {# multi-axioms #}
    {% for ax in ir.multi_axioms -%}
    @model_validator(mode="{{ 'before' if ax.check_first else 'after' }}")
    def check_axiom_{{ ax.number }}(self) -> Self:
        """Axiom {{ ax.number }}: {{ ax.title }}. {{ ax.description }}"""
        return self
    {% endfor %}
```

Migration path that won’t blow things up

Step 1: Build the IR builder in Python reading your current XML/ODXML (lxml or xmltodict).

Step 2: Port only DeriveTypes to Python+Jinja, keep Enum/Init/Test XSLTs as-is.

Step 3: Add golden tests comparing new output to the current (fixing known-bad stubs).



Step 4: Swap your XmlXsltTransform step in aicapture.json for a python derive-types CLI with the same inputs/outputs.

If you want, I can sketch a tiny python derive-types CLI that drops into your pipeline and demonstrates the IR + Jinja flow for one type (e.g., report.002) so you can judge the readability delta.

### More on Goldens
Golden tests (also called snapshot tests) are “expected output” files we commit to the repo. Our generator runs in a test, produces fresh output, and the test asserts that it matches the committed golden. If you intentionally change the generator, you re-generate and update the golden(s) in one step.