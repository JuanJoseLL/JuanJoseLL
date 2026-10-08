# JJ—LAB · cómo se construye este perfil

Cada imagen del perfil es un SVG generado con Python: sin capturas, sin plantillas y sin fuentes web.

| Archivo | Qué dibuja |
| :--- | :--- |
| `lab/hero.py` | El experimento de doble rendija. Las posiciones de las partículas se muestrean dentro de los glifos reales del nombre. |
| `lab/detector.py` | El detector de actividad. Consulta la API GraphQL de GitHub y dibuja un año de contribuciones como un detector de partículas. |
| `lab/arsenal.py` | La tabla periódica del stack (versión de escritorio y móvil). |
| `lab/experiments.py` | Las tarjetas animadas de los proyectos. |
| `lab/cinema.py` · `lab/signature.py` | Fuera del editor, botones, easter egg y cierre. |
| `lab/type.py` | Tipografía: HarfBuzz da forma al texto y cada glifo se convierte en un trazado vectorial. |
| `lab/theme.py` | Paleta, textura y estructura común. |

GitHub muestra las imágenes del README en un entorno aislado, así que el texto no puede depender de `@font-face`. Por eso cada letra se dibuja desde las fuentes incluidas en `lab/fonts/` (Space Grotesk, JetBrains Mono e Instrument Serif, todas con licencia SIL OFL).

## Reconstruir

```bash
brew install librsvg                    # solo para el hero
pip install -r scripts/requirements.txt
python3 scripts/build.py                # todo
python3 scripts/build.py live           # solo el detector
```

El detector se actualiza solo cada noche con [`.github/workflows/detector.yml`](../.github/workflows/detector.yml). También puedes lanzarlo a mano desde la pestaña **Actions**.
