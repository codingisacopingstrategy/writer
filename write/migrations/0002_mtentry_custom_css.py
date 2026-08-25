from django.db import migrations, models

AS_PAGE_CSS = """article p:has(> .as-page) {
  max-width: none;
  padding: 0;
  text-indent: 0;
}
article .as-page {
  position: relative;
  width: 100%;
  max-width: none;
  height: 0;
  padding-bottom: 126.14107884%;
  container-type: inline-size;
  overflow: visible;
  margin: 0;
  --u: calc(100cqw / 1205);
}
article .as-g,
article .as-t {
  position: absolute;
  left: calc(var(--x, 0) * var(--u));
  top: calc(var(--y, 0) * var(--u));
}
article .as-g {
  width: 0;
  height: 0;
  transform-origin: 0 0;
}
article .as-t {
  margin: 0;
  padding: 0;
  border: 0;
  max-width: none;
  text-indent: 0;
  white-space: nowrap;
  line-height: 1;
  font-weight: normal;
  font-style: normal;
  letter-spacing: 0;
  color: #0058ed;
  font-size: calc(var(--fs) * var(--u));
  transform: translateY(-0.8em);
  transform-origin: 0 0;
  user-select: text;
  pointer-events: auto;
}
article .as-t-din {
  font-family: DINdong, sans-serif;
}
article .as-t-cro {
  font-family: Croisant, Croissant, sans-serif;
  paint-order: stroke fill;
  -webkit-text-stroke-color: #000;
  -webkit-text-stroke-width: calc(var(--sw, 0) * var(--u));
}
article .as-t-hel {
  font-family: Helvetica, Arial, sans-serif;
  paint-order: stroke fill;
  -webkit-text-stroke-color: #000;
  -webkit-text-stroke-width: calc(var(--sw, 0) * var(--u));
}
article .as-shape {
  position: absolute;
  left: 0;
  top: 0;
  display: block;
  overflow: visible;
  pointer-events: none;
  width: calc(var(--w) * var(--u));
  height: calc(var(--h) * var(--u));
}
"""


def add_as_page_css(apps, schema_editor):
    MtEntry = apps.get_model("write", "MtEntry")
    MtEntry.objects.filter(slug="smartphones-never-die").update(custom_css=AS_PAGE_CSS)


def remove_as_page_css(apps, schema_editor):
    MtEntry = apps.get_model("write", "MtEntry")
    MtEntry.objects.filter(slug="smartphones-never-die").update(custom_css="")


class Migration(migrations.Migration):

    dependencies = [
        ("write", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="mtentry",
            name="custom_css",
            field=models.TextField(blank=True),
        ),
        migrations.RunPython(add_as_page_css, remove_as_page_css),
    ]
