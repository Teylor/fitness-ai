"""Generate self-contained interactive HTML artifacts for Hermes GUI and web routes."""

from typing import Optional

VALID_FORM_TYPES = ("hub", "meal", "recipe", "ingredient", "workout", "exercise", "summary")


def generate_html(form_type: Optional[str] = "hub") -> str:
    """Generate self-contained interactive HTML artifact.

    Args:
        form_type: One of 'hub', 'meal', 'recipe', 'ingredient', 'workout', 'summary'.
                   Defaults to 'hub'. If a specific form type is chosen, that tab is activated.

    Returns:
        Full HTML5 document string with embedded CSS and vanilla JS.
    """
    active_tab = form_type.lower() if form_type and form_type.lower() in VALID_FORM_TYPES else "hub"
    if active_tab == "hub":
        active_tab = "meal"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Fitness AI - Hermes Hub</title>
  <link rel="icon" type="image/x-icon" href="/favicon.ico?v=2">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png?v=2">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png?v=2">
  <style>
    :root {{
      --bg: #0f172a;
      --card-bg: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #10b981;
      --primary-hover: #059669;
      --cyan: #06b6d4;
      --danger: #ef4444;
      --warning: #f59e0b;
      --input-bg: #0f172a;
      --radius: 10px;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}

    body {{
      background-color: var(--bg);
      color: var(--text);
      padding: 16px;
      display: flex;
      justify-content: center;
      min-height: 100vh;
    }}

    .container {{
      width: 100%;
      max-width: 820px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 18px;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: var(--radius);
    }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 700;
      font-size: 1.15rem;
      color: var(--primary);
    }}

    .nav-tabs {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      background: var(--card-bg);
      padding: 8px;
      border: 1px solid var(--border);
      border-radius: var(--radius);
    }}

    .tab-btn {{
      flex: 1 1 auto;
      min-width: 110px;
      padding: 10px 14px;
      background: transparent;
      border: 1px solid transparent;
      border-radius: 6px;
      color: var(--text-muted);
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: all 0.2s ease;
    }}

    .tab-btn:hover {{
      color: var(--text);
      background: #33415555;
    }}

    .tab-btn.active {{
      background: var(--primary);
      color: #042f2e;
    }}

    .tab-content {{
      display: none;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 20px;
    }}

    .tab-content.active {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    h2 {{
      font-size: 1.25rem;
      color: var(--cyan);
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .form-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 12px;
    }}

    .form-group {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    label {{
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-muted);
    }}

    input, select, textarea {{
      background: var(--input-bg);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 10px 12px;
      border-radius: 6px;
      font-size: 0.95rem;
      outline: none;
    }}

    input:focus, select:focus, textarea:focus {{
      border-color: var(--primary);
    }}

    .btn {{
      padding: 11px 18px;
      background: var(--primary);
      color: #042f2e;
      border: none;
      border-radius: 6px;
      font-weight: 700;
      font-size: 0.95rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: background 0.2s;
    }}

    .btn:hover {{
      background: var(--primary-hover);
    }}

    .btn-secondary {{
      background: #334155;
      color: var(--text);
    }}

    .btn-secondary:hover {{
      background: #475569;
    }}

    .btn-danger {{
      background: var(--danger);
      color: #fff;
    }}

    .btn-sm {{
      padding: 6px 10px;
      font-size: 0.8rem;
    }}

    .table-container {{
      overflow-x: auto;
      margin-top: 8px;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
    }}

    th, td {{
      padding: 8px 10px;
      text-align: left;
      border-bottom: 1px solid var(--border);
    }}

    th {{
      color: var(--text-muted);
      font-weight: 600;
    }}

    #exercises-catalog-table {{
      font-size: 0.84rem;
    }}

    #exercises-catalog-table th,
    #exercises-catalog-table td {{
      padding: 6px 6px;
      vertical-align: middle;
    }}

    #exercises-catalog-table .badge {{
      font-size: 0.72rem;
      padding: 2px 6px;
    }}

    .badge {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: 700;
    }}

    .badge-ok {{ background: #064e3b; color: #6ee7b7; }}
    .badge-info {{ background: #164e63; color: #67e8f9; }}
    .badge-danger {{ background: #7f1d1d; color: #fca5a5; }}
    .badge-warning {{ background: #78350f; color: #fde68a; }}

    .macro-preview {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
      gap: 8px;
      background: var(--input-bg);
      padding: 12px;
      border-radius: 6px;
      border: 1px solid var(--border);
    }}

    .macro-stat {{
      text-align: center;
    }}

    .macro-val {{
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--primary);
    }}

    .macro-lbl {{
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
    }}

    .result-box {{
      display: none;
      padding: 14px;
      border-radius: 6px;
      border: 1px solid var(--border);
      background: #022c22;
      color: #a7f3d0;
      font-size: 0.9rem;
      flex-direction: column;
      gap: 8px;
    }}

    .copy-area {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #0f172a;
      padding: 8px 12px;
      border-radius: 4px;
      font-family: monospace;
      font-size: 0.85rem;
      color: #94a3b8;
      overflow-x: auto;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="brand">
        <span>⚡</span> Fitness AI Hub
      </div>
      <div style="display: flex; gap: 8px; align-items: center;">
        <button type="button" class="btn btn-secondary btn-sm" id="btn-header-sync-health" onclick="syncGoogleHealthUI()" title="Sincronizar comidas, sueño y peso con Google Health">☁️ Sincronizar Google Health</button>
      </div>
    </header>

    <!-- Navigation Tabs -->
    <nav class="nav-tabs" role="tablist">
      <button class="tab-btn {'active' if active_tab == 'meal' else ''}" data-tab="meal" onclick="switchTab('meal')">🥗 Comidas</button>
      <button class="tab-btn {'active' if active_tab == 'recipe' else ''}" data-tab="recipe" onclick="switchTab('recipe')">🍲 Recetas</button>
      <button class="tab-btn {'active' if active_tab == 'ingredient' else ''}" data-tab="ingredient" onclick="switchTab('ingredient')">🥑 Ingredientes</button>
      <button class="tab-btn {'active' if active_tab == 'workout' else ''}" data-tab="workout" onclick="switchTab('workout')">🏋️ Entrenamientos</button>
      <button class="tab-btn {'active' if active_tab == 'exercise' else ''}" data-tab="exercise" onclick="switchTab('exercise')">💪 Ejercicios</button>
      <button class="tab-btn {'active' if active_tab == 'summary' else ''}" data-tab="summary" onclick="switchTab('summary')">📊 Resumen</button>
    </nav>

    <!-- TAB 1: MEAL LOGGER -->
    <section id="tab-meal" class="tab-content {'active' if active_tab == 'meal' else ''}">
      <h2>🥗 Registrar Comida</h2>
      <form id="form-meal" onsubmit="submitMeal(event)">
        <div class="form-grid">
          <div class="form-group">
            <label for="meal-date">Fecha</label>
            <input type="date" id="meal-date" required onclick="this.showPicker && this.showPicker()">
          </div>
          <div class="form-group">
            <label for="meal-eating-type">Tipo de Comida</label>
            <select id="meal-eating-type">
              <option value="tentempie" selected>🥪 Tentempié</option>
              <option value="desayuno">☕ Desayuno</option>
              <option value="comida">🍲 Comida</option>
              <option value="merienda">🍎 Merienda</option>
              <option value="cena">🥗 Cena</option>
            </select>
          </div>
          <div class="form-group">
            <label for="meal-item-type">Tipo de Alimento</label>
            <select id="meal-item-type" onchange="updateMealDatalist()">
              <option value="ingredient">Ingrediente</option>
              <option value="recipe">Receta</option>
            </select>
          </div>
          <div class="form-group">
            <label for="meal-item">Nombre (ej: Arroz, Pechuga, Bowl)</label>
            <input type="text" id="meal-item" list="meal-items-datalist" required placeholder="Buscar o escribir alimento..." oninput="onMealItemInput()">
            <datalist id="meal-items-datalist"></datalist>
          </div>
          <div class="form-group">
            <label for="meal-qty">Cantidad</label>
            <input type="number" id="meal-qty" step="any" min="0.1" required placeholder="100">
          </div>
          <div class="form-group">
            <label for="meal-unit">Unidad</label>
            <select id="meal-unit">
              <option value="gr">Gramos (gr)</option>
              <option value="ml">Mililitros (ml)</option>
              <option value="u">Unidades (u)</option>
            </select>
          </div>
        </div>
        <div style="margin-top: 14px; display: flex; gap: 8px;">
          <button type="submit" class="btn">Registrar Ingesta</button>
        </div>
      </form>
      <div id="meal-result" class="result-box"></div>
    </section>

    <!-- TAB 2: RECIPE BUILDER -->
    <section id="tab-recipe" class="tab-content {'active' if active_tab == 'recipe' else ''}">
      <div id="recipe-edit-banner" style="display: none; background: #1e3a8a; color: #bfdbfe; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; align-items: center; justify-content: space-between;">
        <span>✏️ Modo edición: <strong id="recipe-edit-label"></strong> (ID: <span id="recipe-edit-id"></span>)</span>
        <button type="button" class="btn btn-secondary btn-sm" onclick="cancelEditRecipe()">Cancelar Edición</button>
      </div>

      <h2>🍲 Constructor de Recetas</h2>
      <form id="form-recipe" onsubmit="submitRecipe(event)">
        <div class="form-grid">
          <div class="form-group" style="grid-column: 1 / -1;">
            <label for="recipe-name">Nombre de la Receta</label>
            <input type="text" id="recipe-name" required placeholder="Ej: Bowl de Pollo y Arroz...">
          </div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
          <label>Ingredientes de la Receta</label>
          <button type="button" class="btn btn-secondary btn-sm" onclick="addRecipeRow()">+ Añadir Ingrediente</button>
        </div>

        <div class="table-container">
          <table id="recipe-items-table">
            <thead>
              <tr>
                <th>Ingrediente</th>
                <th style="width: 130px;">Cantidad</th>
                <th style="width: 120px;">Unidad</th>
                <th style="width: 50px;"></th>
              </tr>
            </thead>
            <tbody>
              <!-- Dynamic rows -->
            </tbody>
          </table>
        </div>
        <datalist id="recipe-ingredients-datalist"></datalist>

        <div style="margin-top: 14px; display: flex; gap: 8px;">
          <button type="submit" id="btn-submit-recipe" class="btn">Guardar Receta</button>
          <button type="button" id="btn-cancel-recipe" class="btn btn-secondary" style="display: none;" onclick="cancelEditRecipe()">Cancelar Edición</button>
        </div>
      </form>
      <div id="recipe-result" class="result-box"></div>

      <!-- Catálogo de Recetas Guardadas -->
      <div style="margin-top: 24px; border-top: 1px solid var(--border); padding-top: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
          <h3 style="font-size: 1.1rem; color: var(--text);">📋 Recetas Guardadas</h3>
          <div style="display: flex; gap: 8px; align-items: center;">
            <input type="text" id="recipe-search-input" placeholder="Buscar receta..." style="width: 200px; padding: 6px 10px;" oninput="filterRecipes()">
            <button type="button" class="btn btn-secondary btn-sm" onclick="fetchRecipesList()">🔄 Actualizar</button>
          </div>
        </div>
        <div class="table-container">
          <table id="recipes-catalog-table">
            <thead>
              <tr>
                <th>Receta</th>
                <th>Ingredientes</th>
                <th>Kcal</th>
                <th>Macros (P/C/G)</th>
                <th>Precio</th>
                <th style="width: 80px;">Acción</th>
              </tr>
            </thead>
            <tbody id="recipes-catalog-body">
              <!-- Populated via JS -->
            </tbody>
          </table>
        </div>
        <div id="recipes-catalog-empty" style="display: none; color: var(--text-muted); padding: 12px; text-align: center;">No hay recetas guardadas.</div>
      </div>
    </section>

    <!-- TAB 3: INGREDIENT MANAGER -->
    <section id="tab-ingredient" class="tab-content {'active' if active_tab == 'ingredient' else ''}">
      <div id="ing-edit-banner" style="display: none; background: #1e3a8a; color: #bfdbfe; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; align-items: center; justify-content: space-between;">
        <span>✏️ Modo edición: <strong id="ing-edit-label"></strong> (ID: <span id="ing-edit-id"></span>)</span>
        <button type="button" class="btn btn-secondary btn-sm" onclick="cancelEditIngredient()">Cancelar Edición</button>
      </div>

      <h2>🥑 Crear / Editar Ingrediente</h2>
      <form id="form-ingredient" onsubmit="submitIngredient(event)">
        <div class="form-grid">
          <div class="form-group">
            <label for="ing-name">Nombre del Ingrediente</label>
            <input type="text" id="ing-name" required placeholder="Ej: Avena, Huevo, Aceite...">
          </div>
          <div class="form-group">
            <label for="ing-unit">Unidad Base</label>
            <select id="ing-unit">
              <option value="gr">100 Gramos (gr)</option>
              <option value="ml">100 Mililitros (ml)</option>
              <option value="u">1 Unidad (u)</option>
            </select>
          </div>
          <div class="form-group">
            <label for="ing-kcal">Calorías (kcal)</label>
            <input type="number" id="ing-kcal" step="any" min="0" required placeholder="0">
          </div>
          <div class="form-group">
            <label for="ing-protein">Proteína (g)</label>
            <input type="number" id="ing-protein" step="any" min="0" required placeholder="0">
          </div>
          <div class="form-group">
            <label for="ing-carbs">Carbohidratos (g)</label>
            <input type="number" id="ing-carbs" step="any" min="0" required placeholder="0">
          </div>
          <div class="form-group">
            <label for="ing-fat">Grasas (g)</label>
            <input type="number" id="ing-fat" step="any" min="0" required placeholder="0">
          </div>
          <div class="form-group">
            <label for="ing-price">Precio (€ por unidad base)</label>
            <input type="number" id="ing-price" step="any" min="0" placeholder="0.0">
          </div>
          <div class="form-group" style="justify-content: flex-end; padding-bottom: 6px;">
            <label for="ing-is-supplement" style="display: flex; align-items: center; gap: 8px; cursor: pointer; color: var(--text); font-size: 0.9rem;">
              <input type="checkbox" id="ing-is-supplement" style="width: 18px; height: 18px; accent-color: var(--primary); cursor: pointer;">
              <span>💊 Es suplemento (ej: Creatina, Omega 3...)</span>
            </label>
          </div>
        </div>
        <div style="margin-top: 14px; display: flex; gap: 8px;">
          <button type="submit" id="btn-submit-ingredient" class="btn">Guardar Ingrediente</button>
          <button type="button" id="btn-cancel-ingredient" class="btn btn-secondary" style="display: none;" onclick="cancelEditIngredient()">Cancelar Edición</button>
        </div>
      </form>
      <div id="ingredient-result" class="result-box"></div>

      <!-- Catálogo de Ingredientes Guardados -->
      <div style="margin-top: 24px; border-top: 1px solid var(--border); padding-top: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
          <h3 style="font-size: 1.1rem; color: var(--text);">📋 Ingredientes Guardados</h3>
          <div style="display: flex; gap: 8px; align-items: center;">
            <input type="text" id="ing-search-input" placeholder="Buscar ingrediente o suplemento..." style="width: 220px; padding: 6px 10px;" oninput="filterIngredients()">
            <button type="button" class="btn btn-secondary btn-sm" onclick="fetchIngredientsList()">🔄 Actualizar</button>
          </div>
        </div>
        <div class="table-container">
          <table id="ingredients-catalog-table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Unidad</th>
                <th>Kcal</th>
                <th>P (g)</th>
                <th>C (g)</th>
                <th>G (g)</th>
                <th>Precio</th>
                <th>Estado</th>
                <th style="width: 80px;">Acción</th>
              </tr>
            </thead>
            <tbody id="ingredients-catalog-body">
              <!-- Populated via JS -->
            </tbody>
          </table>
        </div>
        <div id="ingredients-catalog-empty" style="display: none; color: var(--text-muted); padding: 12px; text-align: center;">No hay ingredientes guardados.</div>
      </div>

      <!-- Sección aparte: Agua y Suplementos -->
      <div style="margin-top: 24px; border-top: 1px solid var(--border); padding-top: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
          <h3 style="font-size: 1.1rem; color: var(--cyan);">💧💊 Agua y Suplementos</h3>
          <span class="badge badge-info">Agua diaria: 3L (1.25 €)</span>
        </div>
        <div class="table-container">
          <table id="supplements-catalog-table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Unidad / Consumo</th>
                <th>Kcal</th>
                <th>P (g)</th>
                <th>C (g)</th>
                <th>G (g)</th>
                <th>Precio</th>
                <th>Tipo</th>
                <th style="width: 80px;">Acción</th>
              </tr>
            </thead>
            <tbody id="supplements-catalog-body">
              <!-- Populated via JS -->
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- TAB 4: WORKOUT LOGGER -->
    <section id="tab-workout" class="tab-content {'active' if active_tab == 'workout' else ''}">
      <h2>🏋️ Registrar Entrenamiento</h2>
      <form id="form-workout" onsubmit="submitWorkout(event)">
        <div class="form-grid">
          <div class="form-group">
            <label for="workout-date">Fecha y Hora (opcional)</label>
            <input type="datetime-local" id="workout-date" onclick="this.showPicker && this.showPicker()">
          </div>
          <div class="form-group" style="grid-column: 1 / -1;">
            <label for="workout-notes">Notas de la sesión</label>
            <input type="text" id="workout-notes" placeholder="Ej: Push day enfocado en fuerza...">
          </div>
        </div>

        <div style="margin-top: 12px; display: flex; flex-direction: column; gap: 12px;" id="workout-exercises-container">
          <!-- Exercise blocks added dynamically -->
        </div>

        <div style="margin-top: 8px;">
          <button type="button" class="btn btn-secondary btn-sm" onclick="addExerciseBlock()">+ Añadir Ejercicio</button>
        </div>

        <div style="margin-top: 14px; display: flex; gap: 8px;">
          <button type="submit" class="btn">Registrar Sesión</button>
        </div>
      </form>
      <div id="workout-result" class="result-box"></div>
    </section>

    <!-- TAB 5: EXERCISES & PRS -->
    <section id="tab-exercise" class="tab-content {'active' if active_tab == 'exercise' else ''}">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 8px;">
        <h2>💪 Ejercicios y Récords Personales</h2>
        <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
          <input type="text" id="exercise-search-input" placeholder="Buscar ejercicio..." style="width: 180px; padding: 6px 10px;" oninput="filterExercises()">
          <select id="exercise-group-filter" style="width: 160px; padding: 6px 10px;" onchange="filterExercises()">
            <option value="">Todos los grupos</option>
            <!-- Group options are built dynamically from the catalog in JS -->
          </select>
          <button type="button" class="btn btn-secondary btn-sm" onclick="fetchExercisesList()">🔄 Actualizar</button>
          <button type="button" class="btn btn-primary btn-sm" onclick="toggleNewExerciseForm()">+ Nuevo Ejercicio</button>
        </div>
      </div>

      <!-- Formulario para Añadir Ejercicio -->
      <div id="exercise-create-container" style="display: none; margin-bottom: 20px; background: rgba(15, 23, 42, 0.6); padding: 16px; border: 1px solid var(--border); border-radius: var(--radius);">
        <h3 style="font-size: 1rem; margin-bottom: 12px; color: var(--text);">➕ Añadir Nuevo Ejercicio</h3>
        <form id="form-create-exercise" onsubmit="submitNewExercise(event)">
          <div class="form-grid">
            <div class="form-group">
              <label for="new-exercise-name">Nombre del Ejercicio</label>
              <input type="text" id="new-exercise-name" required placeholder="Ej: Press banca con mancuernas">
            </div>
            <div class="form-group">
              <label for="new-exercise-muscle">Grupo Muscular</label>
              <input type="text" id="new-exercise-muscle" placeholder="Ej: pecho, hombro, pierna..." list="exercise-muscle-datalist">
              <datalist id="exercise-muscle-datalist">
                <!-- Filled dynamically from catalog groups in JS -->
              </datalist>
            </div>
            <div class="form-group">
              <label for="new-exercise-type">Tipo de Ejercicio</label>
              <select id="new-exercise-type">
                <option value="weight_reps" selected>Peso y Repeticiones (Fuerza)</option>
                <option value="time">Tiempo (Duración)</option>
                <option value="distance">Distancia</option>
              </select>
            </div>
          </div>
          <div style="margin-top: 12px; display: flex; gap: 8px;">
            <button type="submit" class="btn btn-primary btn-sm">Guardar Ejercicio</button>
            <button type="button" class="btn btn-secondary btn-sm" onclick="toggleNewExerciseForm(false)">Cancelar</button>
          </div>
        </form>
        <div id="exercise-create-result" class="result-box" style="margin-top: 10px;"></div>
      </div>

      <!-- Tabla de Ejercicios y Récords -->
      <div class="table-container">
        <table id="exercises-catalog-table">
          <thead>
            <tr>
              <th>Ejercicio</th>
              <th>Grupo Muscular</th>
              <th>Tipo</th>
              <th>1RM Estimado (PR)</th>
              <th>Récord de Peso (Max Set)</th>
              <th>Editar</th>
            </tr>
          </thead>
          <tbody id="exercises-catalog-body">
            <!-- Populated via JS -->
          </tbody>
        </table>
      </div>
      <div id="exercises-catalog-empty" style="display: none; color: var(--text-muted); padding: 16px; text-align: center;">No hay ejercicios registrados.</div>
    </section>

    <!-- TAB 6: DAILY SUMMARY -->
    <section id="tab-summary" class="tab-content {'active' if active_tab == 'summary' else ''}">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 16px;">
        <h2>📊 Resumen Diario</h2>
        <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
          <input type="date" id="summary-date" style="padding: 6px 10px; width: 160px;" onchange="fetchSummary()" onclick="this.showPicker && this.showPicker()">
          <button type="button" class="btn btn-secondary btn-sm" onclick="fetchSummary()">🔄 Actualizar</button>
          <button type="button" class="btn btn-primary btn-sm" id="btn-sync-health" onclick="syncGoogleHealthUI()">☁️ Sincronizar Google Health</button>
        </div>
      </div>

      <div id="summary-cards" style="display: flex; flex-direction: column; gap: 20px;">
        <!-- 1. Macro Goals, Consumed & Remaining -->
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
            <h3 style="font-size: 0.95rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">🎯 Objetivos vs Consumido vs Restante</h3>
            <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
              <button type="button" class="btn btn-secondary btn-sm" id="btn-toggle-day-off" onclick="toggleDayOffUI()" title="Alternar entre objetivos de Día de Entreno y Day Off">🏋️ Día Entreno</button>
              <button type="button" class="btn btn-secondary btn-sm" id="btn-config-goals" onclick="toggleGoalProfilesPanel()">⚙️ Objetivos</button>
            </div>
          </div>
          <div id="goal-profiles-panel" style="display: none; background: rgba(15, 23, 42, 0.7); border: 1px solid var(--border); border-radius: 8px; padding: 14px; margin-bottom: 12px;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px;">
              <form id="form-goal-training" onsubmit="saveGoalProfile(event, false)" style="display: flex; flex-direction: column; gap: 8px;">
                <div style="font-weight: 700; font-size: 0.85rem; color: var(--primary);">🏋️ Objetivo Día de Entreno (Default)</div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">
                  <div><label style="font-size: 0.72rem;">Kcal</label><input type="number" id="goal-tr-kcal" step="any" min="0" required placeholder="2500"></div>
                  <div><label style="font-size: 0.72rem;">Proteína (g)</label><input type="number" id="goal-tr-protein" step="any" min="0" required placeholder="180"></div>
                  <div><label style="font-size: 0.72rem;">Carbs (g)</label><input type="number" id="goal-tr-carbs" step="any" min="0" required placeholder="280"></div>
                  <div><label style="font-size: 0.72rem;">Grasas (g)</label><input type="number" id="goal-tr-fat" step="any" min="0" required placeholder="70"></div>
                </div>
                <button type="submit" class="btn btn-primary btn-sm" style="align-self: flex-start;">Guardar Entreno</button>
              </form>
              <form id="form-goal-dayoff" onsubmit="saveGoalProfile(event, true)" style="display: flex; flex-direction: column; gap: 8px;">
                <div style="font-weight: 700; font-size: 0.85rem; color: var(--warning);">🏖️ Objetivo Day Off (Descanso)</div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">
                  <div><label style="font-size: 0.72rem;">Kcal</label><input type="number" id="goal-off-kcal" step="any" min="0" required placeholder="2100"></div>
                  <div><label style="font-size: 0.72rem;">Proteína (g)</label><input type="number" id="goal-off-protein" step="any" min="0" required placeholder="180"></div>
                  <div><label style="font-size: 0.72rem;">Carbs (g)</label><input type="number" id="goal-off-carbs" step="any" min="0" required placeholder="180"></div>
                  <div><label style="font-size: 0.72rem;">Grasas (g)</label><input type="number" id="goal-off-fat" step="any" min="0" required placeholder="70"></div>
                </div>
                <button type="submit" class="btn btn-secondary btn-sm" style="align-self: flex-start; border-color: var(--warning); color: #fcd34d;">Guardar Day Off</button>
              </form>
            </div>
          </div>
          <div class="macro-preview" id="summary-macros" style="grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));"></div>
        </div>

        <!-- 2. Health & Activity Metrics (Steps, Sleep, Weight) -->
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h3 style="font-size: 0.95rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">👟 Actividad y Salud</h3>
            <span style="font-size: 0.75rem; color: var(--text-muted);">Métricas del día</span>
          </div>
          <div class="macro-preview" id="summary-health" style="grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));"></div>
        </div>

        <!-- 3. Day's Meals -->
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h3 style="font-size: 0.95rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">🥗 Comidas del Día</h3>
            <span id="summary-spend-badge" class="badge badge-info" style="font-size: 0.8rem;">Gasto: 0.00 €</span>
          </div>
          <div id="summary-meals-container" style="display: flex; flex-direction: column; gap: 12px;"></div>
          <table style="display: none;"><tbody id="summary-meals-body"></tbody></table>
          <div id="summary-meals-empty" style="display: none; color: var(--text-muted); padding: 12px; text-align: center;">No hay comidas registradas para este día.</div>
        </div>

        <!-- 3b. Water & Supplements -->
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h3 style="font-size: 0.95rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">💧💊 Agua y Suplementos</h3>
            <span id="summary-water-supplements-badge" class="badge badge-info" style="font-size: 0.8rem;">Subtotal: 1.25 €</span>
          </div>
          <div id="summary-water-supplements-container" style="display: flex; flex-direction: column; gap: 12px;"></div>
        </div>

        <!-- 4. Day's Workouts -->
        <div>
          <h3 style="font-size: 0.95rem; color: var(--text-muted); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">🏋️ Entrenamientos Realizados</h3>
          <div id="summary-workouts-container" style="display: flex; flex-direction: column; gap: 10px;"></div>
          <div id="summary-workouts-empty" style="display: none; color: var(--text-muted); padding: 12px; text-align: center;">No hay entrenamientos registrados para este día.</div>
        </div>
      </div>

      <div id="summary-result" class="result-box"></div>
    </section>
  </div>

  <script>
    // Tab switching
    function switchTab(tabName) {{
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      const activeBtn = document.querySelector(`.tab-btn[data-tab="${{tabName}}"]`) || Array.from(document.querySelectorAll('.tab-btn')).find(b => b.textContent.toLowerCase().includes(tabName));
      if (activeBtn) activeBtn.classList.add('active');
      const target = document.getElementById('tab-' + tabName);
      if (target) target.classList.add('active');
      if (tabName === 'ingredient') fetchIngredientsList();
      if (tabName === 'recipe') fetchRecipesList();
      if (tabName === 'exercise') fetchExercisesList();
      if (tabName === 'summary') fetchSummary();
    }}

    // Date helpers (ISO for inputs, DD-MM-YYYY for backend)
    function formatTodayIso(withTime = false) {{
      const d = new Date();
      const pad = n => String(n).padStart(2, '0');
      const datePart = `${{d.getFullYear()}}-${{pad(d.getMonth() + 1)}}-${{pad(d.getDate())}}`;
      if (withTime) {{
        return `${{datePart}}T${{pad(d.getHours())}}:${{pad(d.getMinutes())}}`;
      }}
      return datePart;
    }}

    function toBackendDate(val) {{
      if (!val) return '';
      if (/^\\d{{2}}-\\d{{2}}-\\d{{4}}/.test(val)) return val;
      if (/^\\d{{4}}-\\d{{2}}-\\d{{2}}/.test(val)) {{
        const parts = val.split('-');
        return `${{parts[2]}}-${{parts[1]}}-${{parts[0]}}`;
      }}
      return val;
    }}

    function toBackendDateTime(val) {{
      if (!val) return undefined;
      if (val.includes('T')) {{
        const [d, t] = val.split('T');
        return `${{toBackendDate(d)}} ${{t}}`;
      }}
      return toBackendDate(val);
    }}

    document.getElementById('meal-date').value = formatTodayIso(false);
    document.getElementById('workout-date').value = formatTodayIso(true);
    document.getElementById('summary-date').value = formatTodayIso(false);

    // Dynamic Recipe Rows
    function addRecipeRow(name = '', qty = 100, unit = 'gr') {{
      const tbody = document.querySelector('#recipe-items-table tbody');
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><input type="text" class="rec-item-name" list="recipe-ingredients-datalist" required value="${{name}}" placeholder="Buscar ingrediente..." oninput="onRecipeItemInput(this)"></td>
        <td><input type="number" class="rec-item-qty" required value="${{qty}}" min="0.1" step="any"></td>
        <td>
          <select class="rec-item-unit">
            <option value="gr" ${{unit === 'gr' ? 'selected' : ''}}>gr</option>
            <option value="ml" ${{unit === 'ml' ? 'selected' : ''}}>ml</option>
            <option value="u" ${{unit === 'u' ? 'selected' : ''}}>u</option>
          </select>
        </td>
        <td><button type="button" class="btn btn-danger btn-sm" onclick="this.closest('tr').remove()">×</button></td>
      `;
      tbody.appendChild(tr);
    }}
    // Start with 1 clean empty row instead of hardcoded chicken and rice
    addRecipeRow('', 100, 'gr');

    // Dynamic Workout Exercises & Sets
    let exerciseCount = 0;
    function addExerciseBlock(name = '') {{
      exerciseCount++;
      const id = 'ex-' + exerciseCount;
      const container = document.getElementById('workout-exercises-container');
      const div = document.createElement('div');
      div.id = id;
      div.style.cssText = 'background: var(--input-bg); border: 1px solid var(--border); border-radius: 6px; padding: 12px; display: flex; flex-direction: column; gap: 8px;';
      div.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <input type="text" class="ex-name" required value="${{name}}" list="exercises-datalist" style="font-weight: 700; width: 60%;" placeholder="Nombre del ejercicio...">
          <button type="button" class="btn btn-danger btn-sm" onclick="document.getElementById('${{id}}').remove()">Eliminar Ejercicio</button>
        </div>
        <div class="table-container">
          <table class="sets-table">
            <thead><tr><th style="width: 50px;">Set</th><th>Reps</th><th>Peso (kg)</th><th>1RM Est.</th><th style="width: 40px;"></th></tr></thead>
            <tbody></tbody>
          </table>
        </div>
        <button type="button" class="btn btn-secondary btn-sm" style="align-self: flex-start;" onclick="addSetRow('${{id}}')">+ Añadir Serie</button>
      `;
      container.appendChild(div);
      addSetRow(id, 1, '', '');
    }}

    function addSetRow(exBlockId, setNum, reps = '', weight = '') {{
      const tbody = document.querySelector(`#${{exBlockId}} .sets-table tbody`);
      const rowCount = tbody.children.length + 1;
      const num = setNum || rowCount;
      const tr = document.createElement('tr');
      const calc1rm = (w, r) => r === 1 ? w : Math.round(w * (1 + r / 30) * 100) / 100;
      const hasValues = reps !== '' && weight !== '';
      const initial1rm = hasValues ? `${{calc1rm(Number(weight), Number(reps))}} kg` : '-';

      tr.innerHTML = `
        <td><span class="badge badge-info set-num">${{num}}</span></td>
        <td><input type="number" class="set-reps" required value="${{reps}}" placeholder="Reps" min="1" style="width: 80px;" oninput="updateSet1RM(this)"></td>
        <td><input type="number" class="set-weight" required value="${{weight}}" placeholder="kg" step="any" min="0" style="width: 90px;" oninput="updateSet1RM(this)"></td>
        <td><span class="set-1rm" style="color: var(--primary); font-weight: 700;">${{initial1rm}}</span></td>
        <td><button type="button" class="btn btn-danger btn-sm" onclick="this.closest('tr').remove(); renumberSets('${{exBlockId}}');">×</button></td>
      `;
      tbody.appendChild(tr);
    }}

    function updateSet1RM(input) {{
      const tr = input.closest('tr');
      const repsRaw = tr.querySelector('.set-reps').value;
      const weightRaw = tr.querySelector('.set-weight').value;
      if (repsRaw === '' || weightRaw === '') {{
        tr.querySelector('.set-1rm').textContent = '-';
        return;
      }}
      const reps = parseFloat(repsRaw) || 0;
      const weight = parseFloat(weightRaw) || 0;
      const est1rm = reps === 1 ? weight : Math.round(weight * (1 + reps / 30) * 100) / 100;
      tr.querySelector('.set-1rm').textContent = `${{est1rm}} kg`;
    }}

    function renumberSets(exBlockId) {{
      const tbody = document.querySelector(`#${{exBlockId}} .sets-table tbody`);
      Array.from(tbody.children).forEach((tr, idx) => {{
        tr.querySelector('.set-num').textContent = idx + 1;
      }});
    }}
    addExerciseBlock();

    // Universal Dispatch & Result Display
    async function executeAction(toolName, payload, resultElementId, promptDescription) {{
      const resEl = document.getElementById(resultElementId);
      resEl.style.display = 'flex';
      resEl.style.background = '#022c22';
      resEl.style.color = '#a7f3d0';
      resEl.innerHTML = `⏳ Enviando a Fitness AI...`;

      try {{
        const resp = await fetch(`/api/${{toolName}}`, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload)
        }});
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        const data = await resp.json();

        if (data.status === 'ok') {{
          resEl.innerHTML = `
            <strong>✅ Operación completada con éxito</strong>
            <div>${{JSON.stringify(data, null, 2)}}</div>
          `;
          return data;
        }} else {{
          throw new Error(data.message || data.code || 'Error desconocido');
        }}
      }} catch (err) {{
        // Fallback / Offline Hermes prompt copy mode
        resEl.style.background = '#3b1d04';
        resEl.style.color = '#fed7aa';
        resEl.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <strong>ℹ️ Modo Asistente / Hermes Prompt</strong>
            <span class="badge" style="background: #9a3412; color: #ffedd5;">Directo / Copiar</span>
          </div>
          <p style="font-size: 0.85rem;">${{err.message.includes('fetch') ? 'Servidor local no detectado por CORS/Red directa. Puedes copiar el comando para Hermes:' : err.message}}</p>
          <div class="copy-area">
            <span>${{promptDescription}}</span>
            <button class="btn btn-sm" onclick="navigator.clipboard.writeText('${{promptDescription.replace(/'/g, "\\\\'")}}'); this.textContent = '¡Copiado!';">Copiar</button>
          </div>
        `;
        return null;
      }}
    }}

    // Catalogs State
    let allIngredients = [];
    let allRecipes = [];
    let editingIngredientId = null;
    let editingRecipeId = null;

    function showToast(message, type = 'info') {{
      let container = document.getElementById('toast-container');
      if (!container) {{
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 10px; max-width: 380px;';
        document.body.appendChild(container);
      }}
      const toast = document.createElement('div');
      const bg = type === 'ok' ? '#065f46' : (type === 'error' ? '#991b1b' : '#1e3a8a');
      const border = type === 'ok' ? '#059669' : (type === 'error' ? '#dc2626' : '#3b82f6');
      toast.style.cssText = `background: ${{bg}}; border: 1px solid ${{border}}; color: #ffffff; padding: 12px 16px; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.4); font-size: 0.9rem; transition: opacity 0.3s ease; display: flex; align-items: center; justify-content: space-between; gap: 8px;`;
      toast.innerHTML = `<span>${{escapeHtml(message)}}</span><button style="background: none; border: none; color: #fff; cursor: pointer; font-size: 1.1rem; line-height: 1;" onclick="this.parentElement.remove()">×</button>`;
      container.appendChild(toast);
      setTimeout(() => {{
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
      }}, 4000);
    }}

    async function syncGoogleHealthUI() {{
      const btnSummary = document.getElementById('btn-sync-health');
      const btnHeader = document.getElementById('btn-header-sync-health');
      const btns = [btnSummary, btnHeader].filter(Boolean);
      
      btns.forEach(b => {{
        b.disabled = true;
        b.dataset.origText = b.innerHTML;
        b.innerHTML = '⏳ Sincronizando...';
      }});

      const dateInput = document.getElementById('summary-date');
      let targetDate = '';
      if (dateInput && dateInput.value) {{
        const parts = dateInput.value.split('-');
        if (parts.length === 3) targetDate = `${{parts[2]}}-${{parts[1]}}-${{parts[0]}}`;
      }}

      try {{
        const res = await fetch('/api/sync_google_health', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ date: targetDate || undefined }})
        }});
        const data = await res.json();
        if (data.status === 'ok') {{
          const meals = data.meals_synced || 0;
          const steps = data.steps_fetched || 0;
          const sleep = data.sleep_sessions_fetched || 0;
          const weight = data.weight_records_fetched || 0;
          const wtVal = data.latest_weight_kg ? ` (${{data.latest_weight_kg}} kg)` : '';
          showToast(`☁️ Sincronizado con Google Health: ${{meals}} comidas, ${{steps}} pasos, ${{sleep}} sesiones de sueño, ${{weight}} pesos${{wtVal}}`, 'ok');
          await fetchSummary();
        }} else {{
          showToast(data.message || 'Error al sincronizar con Google Health', 'error');
        }}
      }} catch (err) {{
        showToast(`Error de conexión con Google Health: ${{err.message}}`, 'error');
      }} finally {{
        btns.forEach(b => {{
          b.disabled = false;
          b.innerHTML = b.dataset.origText || '☁️ Sincronizar Google Health';
        }});
      }}
    }}

    function escapeHtml(text) {{
      if (text === null || text === undefined) return '';
      return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
    }}

    function updateMealDatalist() {{
      const type = document.getElementById('meal-item-type').value;
      const datalist = document.getElementById('meal-items-datalist');
      if (!datalist) return;
      datalist.innerHTML = '';
      if (type === 'ingredient') {{
        allIngredients.forEach(i => {{
          const opt = document.createElement('option');
          opt.value = i.name;
          opt.label = `${{i.unit}} | ${{i.kcal || 0}} kcal`;
          datalist.appendChild(opt);
        }});
      }} else {{
        allRecipes.forEach(r => {{
          const opt = document.createElement('option');
          opt.value = r.name;
          opt.label = `${{r.kcal || 0}} kcal`;
          datalist.appendChild(opt);
        }});
      }}
    }}

    function onMealItemInput() {{
      const val = (document.getElementById('meal-item').value || '').trim().toLowerCase();
      const type = document.getElementById('meal-item-type').value;
      if (type === 'ingredient') {{
        const matched = allIngredients.find(i => (i.name || '').toLowerCase() === val);
        if (matched && matched.unit) {{
          document.getElementById('meal-unit').value = matched.unit;
        }}
      }}
    }}

    function updateRecipeDatalist() {{
      const datalist = document.getElementById('recipe-ingredients-datalist');
      if (!datalist) return;
      datalist.innerHTML = '';
      allIngredients.forEach(i => {{
        const opt = document.createElement('option');
        opt.value = i.name;
        opt.label = `${{i.unit}} | ${{i.kcal || 0}} kcal`;
        datalist.appendChild(opt);
      }});
    }}

    function onRecipeItemInput(input) {{
      const val = (input.value || '').trim().toLowerCase();
      const matched = allIngredients.find(i => (i.name || '').toLowerCase() === val);
      if (matched && matched.unit) {{
        const tr = input.closest('tr');
        if (tr) {{
          const unitSelect = tr.querySelector('.rec-item-unit');
          if (unitSelect) unitSelect.value = matched.unit;
        }}
      }}
    }}

    // INGREDIENTS CATALOG & EDIT
    async function fetchIngredientsList() {{
      const tbody = document.getElementById('ingredients-catalog-body');
      const emptyMsg = document.getElementById('ingredients-catalog-empty');
      if (!tbody) return;
      try {{
        const resp = await fetch('/api/list_ingredients');
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        const data = await resp.json();
        if (data.status === 'ok') {{
          allIngredients = data.ingredients || [];
          renderIngredientsTable(allIngredients);
          updateRecipeDatalist();
          updateMealDatalist();
        }}
      }} catch (err) {{
        tbody.innerHTML = `<tr><td colspan="9" style="color: var(--text-muted); text-align: center;">No se pudo conectar con el catálogo de ingredientes (${{err.message}}).</td></tr>`;
      }}
    }}

    function renderIngredientsTable(list) {{
      const tbody = document.getElementById('ingredients-catalog-body');
      const suppTbody = document.getElementById('supplements-catalog-body');
      const emptyMsg = document.getElementById('ingredients-catalog-empty');
      if (!tbody) return;
      tbody.innerHTML = '';

      const regularList = (list || []).filter(i => !i.is_supplement);
      const supplementList = (list || []).filter(i => i.is_supplement);

      if (regularList.length === 0) {{
        if (emptyMsg) emptyMsg.style.display = 'block';
      }} else {{
        if (emptyMsg) emptyMsg.style.display = 'none';
        regularList.forEach(ing => {{
          const tr = document.createElement('tr');
          const badge = ing.provisional
            ? '<span class="badge" style="background:#78350f; color:#fde68a;">Provisional</span>'
            : '<span class="badge badge-ok">Confirmado</span>';
          const priceStr = ing.price ? `${{parseFloat(ing.price).toFixed(2)}} €` : '-';
          tr.innerHTML = `
            <td><strong>${{escapeHtml(ing.name)}}</strong></td>
            <td>${{escapeHtml(ing.unit)}}</td>
            <td>${{ing.kcal || 0}}</td>
            <td>${{ing.protein || 0}}</td>
            <td>${{ing.carbs || 0}}</td>
            <td>${{ing.fat || 0}}</td>
            <td>${{priceStr}}</td>
            <td>${{badge}}</td>
            <td style="white-space: nowrap;">
              <button type="button" class="btn btn-secondary btn-sm" onclick="startEditIngredient(${{ing.id}})">✏️ Editar</button>
              <button type="button" class="btn btn-secondary btn-sm" style="background: rgba(239, 68, 68, 0.15); color: #f87171; border-color: rgba(239, 68, 68, 0.3); margin-left: 0.35rem;" onclick="deleteIngredient(${{ing.id}}, '${{escapeHtml(ing.name)}}')">🗑️ Eliminar</button>
            </td>
          `;
          tbody.appendChild(tr);
        }});
      }}

      if (suppTbody) {{
        suppTbody.innerHTML = '';
        const waterTr = document.createElement('tr');
        waterTr.innerHTML = `
          <td><strong>💧 Agua (Consumo diario)</strong></td>
          <td>3 L / día</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>1.25 €</td>
          <td><span class="badge badge-info">💧 Agua</span></td>
          <td style="color: var(--text-muted); font-size: 0.8rem;">Fijo diario</td>
        `;
        suppTbody.appendChild(waterTr);

        supplementList.forEach(ing => {{
          const tr = document.createElement('tr');
          const priceStr = ing.price ? `${{parseFloat(ing.price).toFixed(2)}} €` : '-';
          tr.innerHTML = `
            <td><strong>💊 ${{escapeHtml(ing.name)}}</strong></td>
            <td>${{escapeHtml(ing.unit)}}</td>
            <td>${{ing.kcal || 0}}</td>
            <td>${{ing.protein || 0}}</td>
            <td>${{ing.carbs || 0}}</td>
            <td>${{ing.fat || 0}}</td>
            <td>${{priceStr}}</td>
            <td><span class="badge badge-warning">💊 Suplemento</span></td>
            <td style="white-space: nowrap;">
              <button type="button" class="btn btn-secondary btn-sm" onclick="startEditIngredient(${{ing.id}})">✏️ Editar</button>
              <button type="button" class="btn btn-secondary btn-sm" style="background: rgba(239, 68, 68, 0.15); color: #f87171; border-color: rgba(239, 68, 68, 0.3); margin-left: 0.35rem;" onclick="deleteIngredient(${{ing.id}}, '${{escapeHtml(ing.name)}}')">🗑️ Eliminar</button>
            </td>
          `;
          suppTbody.appendChild(tr);
        }});
      }}
    }}

    async function deleteIngredient(id, name) {{
      if (!confirm(`¿Seguro que deseas eliminar el ingrediente "${{name}}"?`)) return;
      try {{
        const res = await fetch('/api/delete_ingredient', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ ingredient_id: id }})
        }});
        const data = await res.json();
        if (data.status === 'ok') {{
          showToast(`Ingrediente "${{name}}" eliminado correctamente.`, 'ok');
          if (editingIngredientId === id) cancelEditIngredient();
          await fetchIngredientsList();
        }} else {{
          const msg = data.code === 'dependency'
            ? `No se puede eliminar "${{name}}": está siendo utilizado en una o más recetas.`
            : (data.message || 'Error al eliminar');
          showToast(msg, 'error');
        }}
      }} catch (err) {{
        showToast(`Error de conexión al eliminar: ${{err.message}}`, 'error');
      }}
    }}

    function filterIngredients() {{
      const query = (document.getElementById('ing-search-input').value || '').toLowerCase().trim();
      const filtered = allIngredients.filter(i => (i.name || '').toLowerCase().includes(query));
      renderIngredientsTable(filtered);
    }}

    function startEditIngredient(id) {{
      const ing = allIngredients.find(i => i.id === id);
      if (!ing) return;
      editingIngredientId = id;
      document.getElementById('ing-name').value = ing.name || '';
      document.getElementById('ing-unit').value = ing.unit || 'gr';
      document.getElementById('ing-kcal').value = ing.kcal !== undefined ? ing.kcal : 0;
      document.getElementById('ing-protein').value = ing.protein !== undefined ? ing.protein : 0;
      document.getElementById('ing-carbs').value = ing.carbs !== undefined ? ing.carbs : 0;
      document.getElementById('ing-fat').value = ing.fat !== undefined ? ing.fat : 0;
      document.getElementById('ing-price').value = ing.price !== undefined ? ing.price : 0;
      const suppEl = document.getElementById('ing-is-supplement');
      if (suppEl) suppEl.checked = !!ing.is_supplement;

      document.getElementById('ing-edit-label').textContent = ing.name;
      document.getElementById('ing-edit-id').textContent = id;
      document.getElementById('ing-edit-banner').style.display = 'flex';
      document.getElementById('btn-submit-ingredient').textContent = 'Actualizar Ingrediente';
      document.getElementById('btn-cancel-ingredient').style.display = 'inline-block';
      document.getElementById('form-ingredient').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}

    function cancelEditIngredient() {{
      editingIngredientId = null;
      document.getElementById('form-ingredient').reset();
      const suppEl = document.getElementById('ing-is-supplement');
      if (suppEl) suppEl.checked = false;
      document.getElementById('ing-edit-banner').style.display = 'none';
      document.getElementById('btn-submit-ingredient').textContent = 'Guardar Ingrediente';
      document.getElementById('btn-cancel-ingredient').style.display = 'none';
    }}

    // RECIPES CATALOG & EDIT
    async function fetchRecipesList() {{
      const tbody = document.getElementById('recipes-catalog-body');
      const emptyMsg = document.getElementById('recipes-catalog-empty');
      if (!tbody) return;
      try {{
        const resp = await fetch('/api/list_recipes');
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        const data = await resp.json();
        if (data.status === 'ok') {{
          allRecipes = data.recipes || [];
          renderRecipesTable(allRecipes);
          updateMealDatalist();
        }}
      }} catch (err) {{
        tbody.innerHTML = `<tr><td colspan="6" style="color: var(--text-muted); text-align: center;">No se pudo conectar con el catálogo de recetas (${{err.message}}).</td></tr>`;
      }}
    }}

    function renderRecipesTable(list) {{
      const tbody = document.getElementById('recipes-catalog-body');
      const emptyMsg = document.getElementById('recipes-catalog-empty');
      if (!tbody) return;
      tbody.innerHTML = '';
      if (!list || list.length === 0) {{
        if (emptyMsg) emptyMsg.style.display = 'block';
        return;
      }}
      if (emptyMsg) emptyMsg.style.display = 'none';
      list.forEach(rec => {{
        const tr = document.createElement('tr');
        const itemsStr = (rec.items && rec.items.length > 0)
          ? rec.items.map(it => `${{it.quantity}}${{it.unit}} ${{escapeHtml(it.name || ('Ingrediente #' + it.ingredient_id))}}`).join(', ')
          : '<em style="color: var(--text-muted);">Sin ingredientes / Opaca</em>';
        const kcalStr = rec.kcal !== null && rec.kcal !== undefined ? rec.kcal : '-';
        const p = rec.protein !== null && rec.protein !== undefined ? rec.protein : 0;
        const c = rec.carbs !== null && rec.carbs !== undefined ? rec.carbs : 0;
        const f = rec.fat !== null && rec.fat !== undefined ? rec.fat : 0;
        const macrosStr = `${{p}}g / ${{c}}g / ${{f}}g`;
        const priceStr = rec.price ? `${{parseFloat(rec.price).toFixed(2)}} €` : '-';

        tr.innerHTML = `
          <td><strong>${{escapeHtml(rec.name)}}</strong></td>
          <td style="max-width: 250px; font-size: 0.85rem; color: var(--text-muted);">${{itemsStr}}</td>
          <td>${{kcalStr}}</td>
          <td>${{macrosStr}}</td>
          <td>${{priceStr}}</td>
          <td style="white-space: nowrap;">
            <button type="button" class="btn btn-secondary btn-sm" onclick="startEditRecipe(${{rec.id}})">✏️ Editar</button>
            <button type="button" class="btn btn-secondary btn-sm" style="background: rgba(239, 68, 68, 0.15); color: #f87171; border-color: rgba(239, 68, 68, 0.3); margin-left: 0.35rem;" onclick="deleteRecipe(${{rec.id}}, '${{escapeHtml(rec.name)}}')">🗑️ Eliminar</button>
          </td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    async function deleteRecipe(id, name) {{
      if (!confirm(`¿Seguro que deseas eliminar la receta "${{name}}"?`)) return;
      try {{
        const res = await fetch('/api/delete_recipe', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ recipe_id: id }})
        }});
        const data = await res.json();
        if (data.status === 'ok') {{
          showToast(`Receta "${{name}}" eliminada correctamente.`, 'ok');
          if (editingRecipeId === id) cancelEditRecipe();
          await fetchRecipesList();
        }} else {{
          showToast(data.message || 'Error al eliminar receta', 'error');
        }}
      }} catch (err) {{
        showToast(`Error de conexión al eliminar: ${{err.message}}`, 'error');
      }}
    }}

    function filterRecipes() {{
      const query = (document.getElementById('recipe-search-input').value || '').toLowerCase().trim();
      const filtered = allRecipes.filter(r => (r.name || '').toLowerCase().includes(query));
      renderRecipesTable(filtered);
    }}

    function startEditRecipe(id) {{
      const rec = allRecipes.find(r => r.id === id);
      if (!rec) return;
      editingRecipeId = id;
      document.getElementById('recipe-name').value = rec.name || '';

      const tbody = document.querySelector('#recipe-items-table tbody');
      tbody.innerHTML = '';
      if (rec.items && rec.items.length > 0) {{
        rec.items.forEach(it => {{
          addRecipeRow(it.name || ('Ingrediente #' + it.ingredient_id), it.quantity, it.unit);
        }});
      }} else {{
        addRecipeRow('', 100, 'gr');
      }}

      document.getElementById('recipe-edit-label').textContent = rec.name;
      document.getElementById('recipe-edit-id').textContent = id;
      document.getElementById('recipe-edit-banner').style.display = 'flex';
      document.getElementById('btn-submit-recipe').textContent = 'Actualizar Receta';
      document.getElementById('btn-cancel-recipe').style.display = 'inline-block';
      document.getElementById('form-recipe').scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}

    function cancelEditRecipe() {{
      editingRecipeId = null;
      document.getElementById('form-recipe').reset();
      const tbody = document.querySelector('#recipe-items-table tbody');
      tbody.innerHTML = '';
      addRecipeRow('', 100, 'gr');
      document.getElementById('recipe-edit-banner').style.display = 'none';
      document.getElementById('btn-submit-recipe').textContent = 'Guardar Receta';
      document.getElementById('btn-cancel-recipe').style.display = 'none';
    }}

    // EXERCISES CATALOG & PR TRACKING
    let allExercises = [];

    async function fetchExercisesList() {{
      const tbody = document.getElementById('exercises-catalog-body');
      const emptyMsg = document.getElementById('exercises-catalog-empty');
      if (!tbody) return;
      try {{
        const resp = await fetch('/api/list_exercises?include_prs=true');
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        const data = await resp.json();
        if (data.status === 'ok') {{
          allExercises = data.exercises || [];
          renderExercisesTable(allExercises);
          updateExerciseDatalist();
          updateExerciseGroupFilter();
        }}
      }} catch (err) {{
        tbody.innerHTML = `<tr><td colspan="6" style="color: var(--text-muted); text-align: center;">No se pudo conectar con el catálogo de ejercicios (${{err.message}}).</td></tr>`;
      }}
    }}

    function updateExerciseDatalist() {{
      let dl = document.getElementById('exercises-datalist');
      if (!dl) {{
        dl = document.createElement('datalist');
        dl.id = 'exercises-datalist';
        document.body.appendChild(dl);
      }}
      dl.innerHTML = '';
      allExercises.forEach(ex => {{
        const opt = document.createElement('option');
        opt.value = ex.name;
        dl.appendChild(opt);
      }});

      // Muscle group datalists: predefined options + unique groups present in the catalog
      const groups = allMuscleGroupOptions();
      let muscleDl = document.getElementById('exercise-muscle-datalist');
      if (!muscleDl) {{
        muscleDl = document.createElement('datalist');
        muscleDl.id = 'exercise-muscle-datalist';
        document.body.appendChild(muscleDl);
      }}
      muscleDl.innerHTML = '';
      groups.forEach(g => {{
        const opt = document.createElement('option');
        opt.value = g;
        muscleDl.appendChild(opt);
      }});
      let gdl = document.getElementById('muscle-group-datalist');
      if (!gdl) {{
        gdl = document.createElement('datalist');
        gdl.id = 'muscle-group-datalist';
        document.body.appendChild(gdl);
      }}
      gdl.innerHTML = '';
      groups.forEach(g => {{
        const opt = document.createElement('option');
        opt.value = g;
        gdl.appendChild(opt);
      }});
    }}

    const DEFAULT_MUSCLE_GROUPS = ['Pecho', 'Hombro', 'Biceps', 'Triceps', 'Espalda', 'Pierna'];

    function allMuscleGroupOptions() {{
      const seen = new Set();
      const opts = [];
      DEFAULT_MUSCLE_GROUPS.forEach(g => {{
        const key = g.toLowerCase();
        if (!seen.has(key)) {{
          seen.add(key);
          opts.push(g);
        }}
      }});
      catalogGroups().forEach(g => {{
        const key = g.toLowerCase();
        if (key !== 'unknown' && !seen.has(key)) {{
          seen.add(key);
          opts.push(g);
        }}
      }});
      return opts;
    }}

    function catalogGroups() {{
      const seen = new Set();
      const groups = [];
      allExercises.forEach(ex => {{
        const raw = (ex.muscle_group || '').trim();
        const g = raw.toLowerCase();
        if (g && !seen.has(g)) {{
          seen.add(g);
          groups.push(raw);
        }}
      }});
      groups.sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
      return groups;
    }}

    function updateExerciseGroupFilter() {{
      const sel = document.getElementById('exercise-group-filter');
      if (!sel) return;
      const current = sel.value;
      const groups = catalogGroups();
      const values = new Set(groups.map(g => g.toLowerCase()));
      sel.innerHTML = '<option value="">Todos los grupos</option>';
      groups.forEach(g => {{
        const opt = document.createElement('option');
        opt.value = g;
        opt.textContent = g.toLowerCase() === 'unknown' ? 'Otros' : g;
        sel.appendChild(opt);
      }});
      if (current && values.has(current.toLowerCase())) sel.value = current;
    }}

    function filterExercises() {{
      const search = (document.getElementById('exercise-search-input')?.value || '').trim().toLowerCase();
      const group = (document.getElementById('exercise-group-filter')?.value || '').trim().toLowerCase();

      const filtered = allExercises.filter(ex => {{
        const matchSearch = !search || (ex.name && ex.name.toLowerCase().includes(search));
        const matchGroup = !group || (ex.muscle_group && ex.muscle_group.toLowerCase() === group);
        return matchSearch && matchGroup;
      }});
      renderExercisesTable(filtered);
    }}

    function renderExercisesTable(list) {{
      const tbody = document.getElementById('exercises-catalog-body');
      const emptyMsg = document.getElementById('exercises-catalog-empty');
      if (!tbody) return;
      tbody.innerHTML = '';
      if (!list || list.length === 0) {{
        if (emptyMsg) emptyMsg.style.display = 'block';
        return;
      }}
      if (emptyMsg) emptyMsg.style.display = 'none';

      list.forEach(ex => {{
        const tr = document.createElement('tr');
        const muscle = ex.muscle_group && ex.muscle_group !== 'unknown' ? ex.muscle_group : 'General';

        let typeBadge = '<span class="badge badge-info">Peso/Reps</span>';
        if (ex.type === 'time') {{
          typeBadge = '<span class="badge" style="background: #1e3a8a; color: #93c5fd;">Tiempo</span>';
        }} else if (ex.type === 'distance') {{
          typeBadge = '<span class="badge" style="background: #4c1d95; color: #c4b5fd;">Distancia</span>';
        }}

        let prHtml = '<span style="color: var(--text-muted);">-</span>';
        let maxWeightHtml = '<span style="color: var(--text-muted);">-</span>';

        if (ex.pr) {{
          if (ex.pr.estimated_1rm) {{
            const e1rmDate = ex.pr.estimated_1rm_date ? `<div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 2px;">${{escapeHtml(ex.pr.estimated_1rm_date)}}</div>` : '';
            prHtml = `
              <div style="display: inline-flex; flex-direction: column;">
                <span class="badge badge-ok">🏆 ${{ex.pr.estimated_1rm}} kg</span>
                ${{e1rmDate}}
              </div>
            `;
          }}
          if (ex.pr.max_weight !== undefined && ex.pr.max_weight !== null) {{
            const maxDate = ex.pr.max_weight_date ? `<div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 2px;">${{escapeHtml(ex.pr.max_weight_date)}}</div>` : '';
            maxWeightHtml = `
              <div style="display: inline-flex; flex-direction: column;">
                <span class="badge badge-warning">💪 ${{ex.pr.max_weight}}×${{ex.pr.max_weight_reps || 1}}</span>
                ${{maxDate}}
              </div>
            `;
          }}
        }}

        const muscleValue = (ex.muscle_group || 'unknown');
        const muscleKey = muscleValue.toLowerCase();
        const groupOpts = allMuscleGroupOptions();
        const muscleSelectOpts = groupOpts.map(g =>
          `<option value="${{escapeHtml(g)}}"${{g.toLowerCase() === muscleKey ? ' selected' : ''}}>${{escapeHtml(g)}}</option>`
        ).join('') + `<option value="unknown"${{muscleKey === 'unknown' ? ' selected' : ''}}>Otros</option>`;

        tr.innerHTML = `
          <td><strong style="color: var(--text); font-size: 0.88rem;">${{escapeHtml(ex.name)}}</strong></td>
          <td><span class="badge" style="background: #334155; color: #cbd5e1; text-transform: capitalize;">${{escapeHtml(muscle)}}</span></td>
          <td>${{typeBadge}}</td>
          <td>${{prHtml}}</td>
          <td>${{maxWeightHtml}}</td>
          <td>
            <div style="display: flex; gap: 4px; align-items: center;">
              <select class="ex-edit-muscle" style="width: 92px; padding: 3px 4px; font-size: 0.78rem;">
                ${{muscleSelectOpts}}
              </select>
              <select class="ex-edit-type" style="width: 84px; padding: 3px 4px; font-size: 0.78rem;">
                <option value="weight_reps"${{ex.type === 'weight_reps' ? ' selected' : ''}}>Peso/Reps</option>
                <option value="time"${{ex.type === 'time' ? ' selected' : ''}}>Tiempo</option>
                <option value="distance"${{ex.type === 'distance' ? ' selected' : ''}}>Distancia</option>
              </select>
              <button type="button" class="btn btn-sm btn-secondary" style="padding: 3px 6px; font-size: 0.78rem;" onclick="saveExerciseEdit(${{ex.id}}, this)">💾</button>
            </div>
          </td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function toggleNewExerciseForm(force) {{
      const container = document.getElementById('exercise-create-container');
      if (!container) return;
      const isVisible = container.style.display !== 'none';
      const show = force !== undefined ? force : !isVisible;
      container.style.display = show ? 'block' : 'none';
      if (show) {{
        document.getElementById('new-exercise-name')?.focus();
      }}
    }}

    async function saveExerciseEdit(exerciseId, btn) {{
      const tr = btn ? btn.closest('tr') : null;
      if (!tr) return;
      const muscleInput = tr.querySelector('.ex-edit-muscle');
      const typeSelect = tr.querySelector('.ex-edit-type');
      const payload = {{
        exercise_id: exerciseId,
        muscle_group: (muscleInput ? muscleInput.value.trim() : '') || 'unknown',
        type: typeSelect ? typeSelect.value : 'weight_reps'
      }};
      const original = btn.textContent;
      btn.disabled = true;
      btn.textContent = '...';
      try {{
        const resp = await fetch('/api/update_exercise', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload)
        }});
        const data = await resp.json();
        if (data.status === 'ok') {{
          btn.textContent = '✅';
          await fetchExercisesList();
        }} else {{
          btn.textContent = '❌';
        }}
      }} catch (err) {{
        btn.textContent = '❌';
      }}
      setTimeout(() => {{
        btn.textContent = original;
        btn.disabled = false;
      }}, 1500);
    }}

    async function submitNewExercise(e) {{
      e.preventDefault();
      const name = (document.getElementById('new-exercise-name')?.value || '').trim();
      const muscle = (document.getElementById('new-exercise-muscle')?.value || '').trim() || 'unknown';
      const type = document.getElementById('new-exercise-type')?.value || 'weight_reps';

      if (!name) return;
      const payload = {{ name: name, muscle_group: muscle, type: type }};
      const prompt = `Crea el ejercicio "${{name}}" (grupo: ${{muscle}}, tipo: ${{type}})`;
      const res = await executeAction('create_exercise', payload, 'exercise-create-result', prompt);
      if (res && res.status === 'ok') {{
        document.getElementById('form-create-exercise').reset();
        setTimeout(() => toggleNewExerciseForm(false), 1200);
        await fetchExercisesList();
      }}
    }}

    // Form handlers
    function submitMeal(e) {{
      e.preventDefault();
      const rawDate = document.getElementById('meal-date').value;
      const formattedDate = toBackendDate(rawDate);
      const payload = {{
        date: formattedDate,
        item_name: document.getElementById('meal-item').value,
        item_type: document.getElementById('meal-item-type').value,
        meal_type: document.getElementById('meal-eating-type').value,
        quantity: parseFloat(document.getElementById('meal-qty').value),
        unit: document.getElementById('meal-unit').value,
        async_sync: true
      }};
      const prompt = `Registra una comida (${{payload.meal_type}}) de ${{payload.quantity}} ${{payload.unit}} de ${{payload.item_name}} para la fecha ${{payload.date}}`;
      executeAction('register_meal', payload, 'meal-result', prompt);
    }}

    async function submitIngredient(e) {{
      e.preventDefault();
      const isUpdating = editingIngredientId !== null;
      const isSupplement = !!document.getElementById('ing-is-supplement')?.checked;
      const payload = {{
        name: document.getElementById('ing-name').value,
        unit: document.getElementById('ing-unit').value,
        kcal: parseFloat(document.getElementById('ing-kcal').value) || 0,
        protein: parseFloat(document.getElementById('ing-protein').value) || 0,
        carbs: parseFloat(document.getElementById('ing-carbs').value) || 0,
        fat: parseFloat(document.getElementById('ing-fat').value) || 0,
        price: parseFloat(document.getElementById('ing-price').value) || 0,
        is_supplement: isSupplement
      }};
      let toolName = 'create_ingredient';
      let prompt = `Crea el ingrediente ${{payload.name}} (${{payload.unit}}): ${{payload.kcal}} kcal, ${{payload.protein}}g P, ${{payload.carbs}}g C, ${{payload.fat}}g G`;
      if (isUpdating) {{
        toolName = 'update_ingredient';
        payload.ingredient_id = editingIngredientId;
        prompt = `Actualiza el ingrediente ID ${{editingIngredientId}} (${{payload.name}}): ${{payload.kcal}} kcal, ${{payload.protein}}g P, ${{payload.carbs}}g C, ${{payload.fat}}g G, ${{payload.price}}€`;
      }}
      const res = await executeAction(toolName, payload, 'ingredient-result', prompt);
      if (res && res.status === 'ok') {{
        await fetchIngredientsList();
        if (isUpdating) {{
          cancelEditIngredient();
        }}
      }}
    }}

    async function submitRecipe(e) {{
      e.preventDefault();
      const isUpdating = editingRecipeId !== null;
      const items = [];
      document.querySelectorAll('#recipe-items-table tbody tr').forEach(tr => {{
        items.push({{
          name: tr.querySelector('.rec-item-name').value,
          quantity: parseFloat(tr.querySelector('.rec-item-qty').value) || 0,
          unit: tr.querySelector('.rec-item-unit').value
        }});
      }});
      let toolName = 'create_recipe';
      const payload = {{
        name: document.getElementById('recipe-name').value,
        ingredients: items
      }};
      let prompt = `Crea la receta ${{payload.name}} con ingredientes: ` + items.map(i => `${{i.quantity}} ${{i.unit}} de ${{i.name}}`).join(', ');
      if (isUpdating) {{
        toolName = 'update_recipe';
        payload.recipe_id = editingRecipeId;
        prompt = `Actualiza la receta ID ${{editingRecipeId}} (${{payload.name}}) con ingredientes: ` + items.map(i => `${{i.quantity}} ${{i.unit}} de ${{i.name}}`).join(', ');
      }}
      const res = await executeAction(toolName, payload, 'recipe-result', prompt);
      if (res && res.status === 'ok') {{
        await fetchRecipesList();
        if (isUpdating) {{
          cancelEditRecipe();
        }}
      }}
    }}

    function submitWorkout(e) {{
      e.preventDefault();
      const exercises = [];
      document.querySelectorAll('#workout-exercises-container > div').forEach(div => {{
        const exName = div.querySelector('.ex-name').value;
        const sets = [];
        div.querySelectorAll('.sets-table tbody tr').forEach((tr, i) => {{
          sets.push({{
            set_number: i + 1,
            reps: parseInt(tr.querySelector('.set-reps').value) || 1,
            weight: parseFloat(tr.querySelector('.set-weight').value) || 0
          }});
        }});
        exercises.push({{ name: exName, sets }});
      }});
      const rawDate = document.getElementById('workout-date').value;
      const formattedDate = rawDate ? toBackendDateTime(rawDate) : undefined;
      const payload = {{
        date: formattedDate,
        notes: document.getElementById('workout-notes').value || undefined,
        exercises
      }};
      const prompt = `Registra entrenamiento: ` + exercises.map(e => `${{e.name}} (${{e.sets.length}} series)`).join(', ');
      executeAction('register_workout', payload, 'workout-result', prompt);
    }}

    async function fetchSummary() {{
      const rawDate = document.getElementById('summary-date').value;
      const date = toBackendDate(rawDate) || toBackendDate(formatTodayIso(false));
      const resEl = document.getElementById('summary-result');

      try {{
        const [mealResp, woResp, healthResp] = await Promise.all([
          fetch(`/api/get_day_summary?date=${{date}}`).catch(() => null),
          fetch(`/api/get_workouts_by_day?date=${{date}}`).catch(() => null),
          fetch(`/api/get_health_metrics?date=${{date}}`).catch(() => null)
        ]);

        const mealData = mealResp && mealResp.ok ? await mealResp.json() : null;
        const woData = woResp && woResp.ok ? await woResp.json() : null;
        const healthData = healthResp && healthResp.ok ? await healthResp.json() : null;

        if (mealData && mealData.status === 'ok') {{
          renderSummaryNutrition(mealData);
          populateGoalProfiles(mealData.goal_profiles || null);
          renderSummaryMeals(mealData.meals || [], mealData.spend || 0);
          renderSummaryWaterAndSupplements(mealData.water_and_supplements || null, mealData.meals || []);
        }} else {{
          renderSummaryNutrition({{}});
          renderSummaryMeals([], 1.25);
          renderSummaryWaterAndSupplements(null, []);
        }}

        if (woData && woData.status === 'ok') {{
          renderSummaryWorkouts(woData.sessions || []);
        }} else {{
          renderSummaryWorkouts([]);
        }}

        if (healthData && healthData.status === 'ok') {{
          renderSummaryHealth(healthData, date);
        }} else {{
          renderSummaryHealth(null, date);
        }}

        resEl.style.display = 'none';
      }} catch (err) {{
        resEl.style.display = 'flex';
        resEl.style.background = '#3b1d04';
        resEl.style.color = '#fed7aa';
        resEl.innerHTML = `ℹ️ Consulta con Hermes: <code>Dame el resumen del día ${{date}}</code> (${{err.message}})`;
      }}
    }}

    let currentSummaryIsDayOff = false;

    function toggleGoalProfilesPanel(force) {{
      const panel = document.getElementById('goal-profiles-panel');
      if (!panel) return;
      const show = force !== undefined ? force : panel.style.display === 'none';
      panel.style.display = show ? 'block' : 'none';
    }}

    function populateGoalProfiles(profiles) {{
      if (!profiles) return;
      const tr = profiles.training_default;
      if (tr) {{
        const k = document.getElementById('goal-tr-kcal');
        const p = document.getElementById('goal-tr-protein');
        const c = document.getElementById('goal-tr-carbs');
        const f = document.getElementById('goal-tr-fat');
        if (k && tr.kcal !== undefined) k.value = tr.kcal;
        if (p && tr.protein !== undefined) p.value = tr.protein;
        if (c && tr.carbs !== undefined) c.value = tr.carbs;
        if (f && tr.fat !== undefined) f.value = tr.fat;
      }}
      const off = profiles.day_off_default;
      if (off) {{
        const k = document.getElementById('goal-off-kcal');
        const p = document.getElementById('goal-off-protein');
        const c = document.getElementById('goal-off-carbs');
        const f = document.getElementById('goal-off-fat');
        if (k && off.kcal !== undefined) k.value = off.kcal;
        if (p && off.protein !== undefined) p.value = off.protein;
        if (c && off.carbs !== undefined) c.value = off.carbs;
        if (f && off.fat !== undefined) f.value = off.fat;
      }}
    }}

    async function saveGoalProfile(e, isDayOff) {{
      e.preventDefault();
      const prefix = isDayOff ? 'goal-off' : 'goal-tr';
      const payload = {{
        kcal: parseFloat(document.getElementById(`${{prefix}}-kcal`).value) || 0,
        protein: parseFloat(document.getElementById(`${{prefix}}-protein`).value) || 0,
        carbs: parseFloat(document.getElementById(`${{prefix}}-carbs`).value) || 0,
        fat: parseFloat(document.getElementById(`${{prefix}}-fat`).value) || 0,
        default: !isDayOff,
        day_off_default: isDayOff
      }};
      try {{
        const res = await fetch('/api/set_daily_goal', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload)
        }});
        const data = await res.json();
        if (data.status === 'ok') {{
          showToast(isDayOff ? '🏖️ Objetivo Day Off guardado.' : '🏋️ Objetivo Día de Entreno guardado.', 'ok');
          await fetchSummary();
        }} else {{
          showToast(data.message || 'Error al guardar objetivos', 'error');
        }}
      }} catch (err) {{
        showToast(`Error de conexión: ${{err.message}}`, 'error');
      }}
    }}

    async function toggleDayOffUI() {{
      const rawDate = document.getElementById('summary-date').value;
      const date = toBackendDate(rawDate) || toBackendDate(formatTodayIso(false));
      const targetState = !currentSummaryIsDayOff;
      try {{
        const res = await fetch('/api/toggle_day_off', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ date: date, is_day_off: targetState }})
        }});
        const data = await res.json();
        if (data.status === 'ok') {{
          showToast(data.is_day_off ? `🏖️ Day Off activado para ${{date}}` : `🏋️ Día de Entreno activado para ${{date}}`, 'ok');
          await fetchSummary();
        }} else if (data.code === 'not_found') {{
          toggleGoalProfilesPanel(true);
          showToast('Configura primero tus objetivos de Day Off en el panel superior.', 'info');
        }} else {{
          showToast(data.message || 'Error al cambiar modo Day Off', 'error');
        }}
      }} catch (err) {{
        showToast(`Error de conexión: ${{err.message}}`, 'error');
      }}
    }}

    function renderSummaryNutrition(data) {{
      const c = data.consumed || {{ kcal: 0, protein: 0, carbs: 0, fat: 0 }};
      const g = data.goal || {{ kcal: 0, protein: 0, carbs: 0, fat: 0 }};
      currentSummaryIsDayOff = !!g.is_day_off;
      const toggleBtn = document.getElementById('btn-toggle-day-off');
      if (toggleBtn) {{
        if (currentSummaryIsDayOff) {{
          toggleBtn.innerHTML = '🏖️ Day Off';
          toggleBtn.style.background = 'rgba(245, 158, 11, 0.2)';
          toggleBtn.style.borderColor = 'var(--warning)';
          toggleBtn.style.color = '#fcd34d';
        }} else {{
          toggleBtn.innerHTML = '🏋️ Día Entreno';
          toggleBtn.style.background = '';
          toggleBtn.style.borderColor = '';
          toggleBtn.style.color = '';
        }}
      }}
      const rem = data.remaining || {{
        kcal: Math.round(((g.kcal || 0) - c.kcal) * 10) / 10,
        protein: Math.round(((g.protein || 0) - c.protein) * 10) / 10,
        carbs: Math.round(((g.carbs || 0) - c.carbs) * 10) / 10,
        fat: Math.round(((g.fat || 0) - c.fat) * 10) / 10
      }};

      const formatCard = (title, consumed, goal, remaining, unit) => {{
        const hasGoal = goal && goal > 0;
        let remText = 'Sin meta';
        let badgeClass = 'badge-info';
        if (hasGoal) {{
          if (remaining >= 0) {{
            remText = `${{remaining}}${{unit}} restantes`;
            badgeClass = 'badge-ok';
          }} else {{
            remText = `${{Math.abs(remaining)}}${{unit}} excedidos ⚠️`;
            badgeClass = 'badge-danger';
          }}
        }}
        const goalLabel = hasGoal ? `Meta: ${{goal}}${{unit}}` : 'Sin meta fijada';
        return `
          <div class="macro-stat" style="background: var(--input-bg); border: 1px solid var(--border); border-radius: 6px; padding: 10px;">
            <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">${{title}}</div>
            <div class="macro-val" style="margin: 4px 0;">${{consumed}}${{unit}}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">${{goalLabel}}</div>
            <div style="margin-top: 6px;"><span class="badge ${{badgeClass}}">${{remText}}</span></div>
          </div>
        `;
      }};

      const container = document.getElementById('summary-macros');
      if (container) {{
        container.innerHTML = `
          ${{formatCard('Calorías', c.kcal, g.kcal, rem.kcal, ' kcal')}}
          ${{formatCard('Proteína', c.protein, g.protein, rem.protein, 'g')}}
          ${{formatCard('Carbohidratos', c.carbs, g.carbs, rem.carbs, 'g')}}
          ${{formatCard('Grasas', c.fat, g.fat, rem.fat, 'g')}}
        `;
      }}
    }}

    function renderSummaryHealth(healthData, date) {{
      const el = document.getElementById('summary-health');
      if (!el) return;
      const steps = healthData && healthData.steps;
      const sleep = healthData && healthData.sleep;
      const weight = healthData && healthData.weight;

      // 1. Steps (pulled exclusively from Google Health)
      let stepsContent = `
        <div style="color: var(--text-muted); font-size: 0.85rem;">Sin registro</div>
        <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 4px;">Sincroniza con Google Health</div>
      `;
      if (steps) {{
        const distStr = steps.distance_km ? ` (${{steps.distance_km}} km)` : '';
        const sourceBadge = '<span style="font-size: 0.65rem; background: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 1px 5px; border-radius: 4px; margin-left: 4px;">Google Health</span>';
        stepsContent = `
          <div class="macro-val" style="color: var(--cyan);">${{Number(steps.steps).toLocaleString()}}</div>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">pasos${{distStr}}${{sourceBadge}}</div>
        `;
      }}

      // 2. Sleep
      let sleepContent = `<div style="color: var(--text-muted); font-size: 0.85rem;">Sin registro</div>`;
      if (sleep) {{
        sleepContent = `
          <div class="macro-val" style="color: #a78bfa;">${{sleep.duration_hours}}h</div>
          <div style="font-size: 0.75rem; color: var(--text-muted);">${{sleep.duration_minutes}} min totales</div>
          <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 4px;">P: ${{sleep.deep_sleep_minutes}}m | REM: ${{sleep.rem_sleep_minutes}}m | L: ${{sleep.light_sleep_minutes}}m</div>
        `;
      }}

      // 3. Weight
      let weightContent = `<div style="color: var(--text-muted); font-size: 0.85rem;">Sin registro</div>`;
      if (weight) {{
        const bmiStr = weight.bmi ? ` | IMC: ${{weight.bmi}}` : '';
        const fatStr = weight.body_fat_pct ? ` | ${{weight.body_fat_pct}}% grasa` : '';
        weightContent = `
          <div class="macro-val" style="color: var(--warning);">${{weight.weight_kg}} kg</div>
          <div style="font-size: 0.75rem; color: var(--text-muted);">Peso corporal${{bmiStr}}${{fatStr}}</div>
        `;
      }}

      el.innerHTML = `
        <div class="macro-stat" style="background: var(--input-bg); border: 1px solid var(--border); border-radius: 6px; padding: 10px;">
          <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">👟 Pasos</div>
          <div style="margin: 6px 0;">${{stepsContent}}</div>
        </div>
        <div class="macro-stat" style="background: var(--input-bg); border: 1px solid var(--border); border-radius: 6px; padding: 10px;">
          <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">💤 Sueño</div>
          <div style="margin: 6px 0;">${{sleepContent}}</div>
        </div>
        <div class="macro-stat" style="background: var(--input-bg); border: 1px solid var(--border); border-radius: 6px; padding: 10px;">
          <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">⚖️ Peso</div>
          <div style="margin: 6px 0;">${{weightContent}}</div>
        </div>
      `;
    }}

    const MEAL_TYPE_SECTIONS = [
      {{ key: 'desayuno', label: 'Desayuno', icon: '☕' }},
      {{ key: 'tentempie', label: 'Tentempié', icon: '🥪' }},
      {{ key: 'comida', label: 'Comida', icon: '🍲' }},
      {{ key: 'merienda', label: 'Merienda', icon: '🍎' }},
      {{ key: 'cena', label: 'Cena', icon: '🥗' }}
    ];

    function renderSummaryMeals(meals, spend) {{
      const container = document.getElementById('summary-meals-container');
      const emptyMsg = document.getElementById('summary-meals-empty');
      const spendBadge = document.getElementById('summary-spend-badge');
      if (spendBadge) {{
        spendBadge.textContent = `Gasto: ${{parseFloat(spend || 0).toFixed(2)}} €`;
      }}
      if (!container) return;
      container.innerHTML = '';

      const regularMeals = (meals || []).filter(m => !m.is_supplement);
      if (regularMeals.length === 0) {{
        if (emptyMsg) emptyMsg.style.display = 'block';
        return;
      }}
      if (emptyMsg) emptyMsg.style.display = 'none';

      MEAL_TYPE_SECTIONS.forEach(sec => {{
        const typeMeals = regularMeals.filter(m => {{
          const mt = (m.meal_type || (m.entry && m.entry.meal_type) || 'tentempie').toLowerCase();
          return mt === sec.key;
        }});

        if (typeMeals.length === 0) return;

        let totalKcal = 0;
        let totalP = 0;
        let totalC = 0;
        let totalF = 0;
        let totalSpend = 0;
        let rowsHtml = '';

        typeMeals.forEach(m => {{
          const entryId = m.entry ? m.entry.id : m.id;
          const name = m.name || (m.entry && (m.entry.item_name || m.entry.item_type)) || 'Alimento';
          const qty = m.quantity || (m.entry && m.entry.quantity) || 0;
          const unit = m.unit || (m.entry && m.entry.unit) || 'gr';
          const price = m.price ? `${{parseFloat(m.price).toFixed(2)}} €` : '-';
          const kcal = m.kcal || 0;
          const p = m.protein || 0;
          const c = m.carbs || 0;
          const f = m.fat || 0;

          totalKcal += kcal;
          totalP += p;
          totalC += c;
          totalF += f;
          if (m.price) totalSpend += parseFloat(m.price);

          const deleteBtn = entryId
            ? `<button type="button" class="btn btn-secondary btn-sm" style="background: rgba(239, 68, 68, 0.15); color: #f87171; border-color: rgba(239, 68, 68, 0.3);" onclick="deleteMeal(${{entryId}}, '${{escapeHtml(name)}}')">🗑️ Eliminar</button>`
            : '-';

          rowsHtml += `
            <tr>
              <td><strong>${{escapeHtml(name)}}</strong></td>
              <td>${{qty}} ${{escapeHtml(unit)}}</td>
              <td>${{kcal}}</td>
              <td>${{p}}g / ${{c}}g / ${{f}}g</td>
              <td>${{price}}</td>
              <td>${{deleteBtn}}</td>
            </tr>
          `;
        }});

        const spendStr = totalSpend > 0 ? ` • ${{totalSpend.toFixed(2)}} €` : '';
        const block = document.createElement('div');
        block.style.cssText = 'background: var(--input-bg); border: 1px solid var(--border); border-radius: 6px; padding: 12px; display: flex; flex-direction: column; gap: 8px;';
        block.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 6px;">
            <div style="font-weight: 700; color: var(--cyan); font-size: 0.95rem;">${{sec.icon}} ${{sec.label}} <span style="font-size: 0.75rem; font-weight: normal; color: var(--text-muted);">(${{typeMeals.length}})</span></div>
            <div style="font-size: 0.8rem; color: var(--text-muted); font-weight: 600;">
              <span style="color: var(--primary); font-weight: 700;">${{Math.round(totalKcal * 10) / 10}} kcal</span> • P: ${{Math.round(totalP * 10) / 10}}g | C: ${{Math.round(totalC * 10) / 10}}g | G: ${{Math.round(totalF * 10) / 10}}g${{spendStr}}
            </div>
          </div>
          <div class="table-container" style="margin-top: 4px;">
            <table>
              <thead>
                <tr>
                  <th>Alimento</th>
                  <th>Cantidad</th>
                  <th>Kcal</th>
                  <th>P / C / G</th>
                  <th>Precio</th>
                  <th>Acción</th>
                </tr>
              </thead>
              <tbody>
                ${{rowsHtml}}
              </tbody>
            </table>
          </div>
        `;
        container.appendChild(block);
      }});
    }}

    function renderSummaryWaterAndSupplements(waterAndSupplements, allMeals) {{
      const container = document.getElementById('summary-water-supplements-container');
      const badge = document.getElementById('summary-water-supplements-badge');
      if (!container) return;
      container.innerHTML = '';

      const supplements = (waterAndSupplements && waterAndSupplements.supplements)
        ? waterAndSupplements.supplements
        : (allMeals || []).filter(m => m.is_supplement);

      let totalKcal = 0;
      let totalP = 0;
      let totalC = 0;
      let totalF = 0;
      let totalSpend = 1.25;

      let rowsHtml = `
        <tr>
          <td><strong>💧 Agua (Consumo diario)</strong></td>
          <td>3 L</td>
          <td>0</td>
          <td>0g / 0g / 0g</td>
          <td>1.25 €</td>
          <td><span class="badge badge-info">Fijo diario</span></td>
        </tr>
      `;

      supplements.forEach(m => {{
        const entryId = m.entry ? m.entry.id : m.id;
        const name = m.name || (m.entry && (m.entry.item_name || m.entry.item_type)) || 'Suplemento';
        const qty = m.quantity || (m.entry && m.entry.quantity) || 0;
        const unit = m.unit || (m.entry && m.entry.unit) || 'gr';
        const price = m.price ? `${{parseFloat(m.price).toFixed(2)}} €` : '-';
        const kcal = m.kcal || 0;
        const p = m.protein || 0;
        const c = m.carbs || 0;
        const f = m.fat || 0;

        totalKcal += kcal;
        totalP += p;
        totalC += c;
        totalF += f;
        if (m.price) totalSpend += parseFloat(m.price);

        const deleteBtn = entryId
          ? `<button type="button" class="btn btn-secondary btn-sm" style="background: rgba(239, 68, 68, 0.15); color: #f87171; border-color: rgba(239, 68, 68, 0.3);" onclick="deleteMeal(${{entryId}}, '${{escapeHtml(name)}}')">🗑️ Eliminar</button>`
          : '-';

        rowsHtml += `
          <tr>
            <td><strong>💊 ${{escapeHtml(name)}}</strong></td>
            <td>${{qty}} ${{escapeHtml(unit)}}</td>
            <td>${{kcal}}</td>
            <td>${{p}}g / ${{c}}g / ${{f}}g</td>
            <td>${{price}}</td>
            <td>${{deleteBtn}}</td>
          </tr>
        `;
      }});

      if (badge) {{
        badge.textContent = `Subtotal: ${{totalSpend.toFixed(2)}} €`;
      }}

      const block = document.createElement('div');
      block.style.cssText = 'background: var(--input-bg); border: 1px solid var(--border); border-radius: 6px; padding: 12px; display: flex; flex-direction: column; gap: 8px;';
      block.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 6px;">
          <div style="font-weight: 700; color: var(--cyan); font-size: 0.95rem;">💧💊 Agua (3L) y Suplementos <span style="font-size: 0.75rem; font-weight: normal; color: var(--text-muted);">(${{1 + supplements.length}})</span></div>
          <div style="font-size: 0.8rem; color: var(--text-muted); font-weight: 600;">
            <span style="color: var(--primary); font-weight: 700;">${{Math.round(totalKcal * 10) / 10}} kcal</span> • P: ${{Math.round(totalP * 10) / 10}}g | C: ${{Math.round(totalC * 10) / 10}}g | G: ${{Math.round(totalF * 10) / 10}}g • ${{totalSpend.toFixed(2)}} €
          </div>
        </div>
        <div class="table-container" style="margin-top: 4px;">
          <table>
            <thead>
              <tr>
                <th>Elemento</th>
                <th>Cantidad</th>
                <th>Kcal</th>
                <th>P / C / G</th>
                <th>Precio</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              ${{rowsHtml}}
            </tbody>
          </table>
        </div>
      `;
      container.appendChild(block);
    }}

    async function deleteMeal(entryId, name) {{
      if (!confirm(`¿Seguro que deseas eliminar la comida "${{name}}"?`)) return;
      try {{
        const res = await fetch('/api/delete_meal', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ entry_id: entryId, async_sync: true }})
        }});
        const data = await res.json();
        if (data.status === 'ok') {{
          showToast(`Comida "${{name}}" eliminada correctamente.`, 'ok');
          await fetchSummary();
        }} else {{
          showToast(data.message || 'Error al eliminar la comida', 'error');
        }}
      }} catch (err) {{
        showToast(`Error de conexión al eliminar comida: ${{err.message}}`, 'error');
      }}
    }}

    function renderSummaryWorkouts(sessions) {{
      const container = document.getElementById('summary-workouts-container');
      const emptyMsg = document.getElementById('summary-workouts-empty');
      if (!container) return;
      container.innerHTML = '';
      if (!sessions || sessions.length === 0) {{
        if (emptyMsg) emptyMsg.style.display = 'block';
        return;
      }}
      if (emptyMsg) emptyMsg.style.display = 'none';
      sessions.forEach((s, idx) => {{
        const div = document.createElement('div');
        div.style.cssText = 'background: var(--input-bg); border: 1px solid var(--border); border-radius: 6px; padding: 12px; display: flex; flex-direction: column; gap: 8px;';
        
        let setsRows = '';
        (s.sets || []).forEach(set => {{
          const e1rm = set.estimated_1rm ? `${{set.estimated_1rm}} kg` : '-';
          setsRows += `
            <tr>
              <td><strong>${{escapeHtml(set.exercise)}}</strong></td>
              <td>Serie ${{set.set_number}}</td>
              <td>${{set.reps}}</td>
              <td>${{set.weight}} kg</td>
              <td><span style="color: var(--primary); font-weight: 700;">${{e1rm}}</span></td>
            </tr>
          `;
        }});

        const notesStr = s.notes ? `<div style="font-size: 0.85rem; color: var(--text-muted);">${{escapeHtml(s.notes)}}</div>` : '';
        div.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 6px;">
            <div style="font-weight: 700; color: var(--cyan);">🏋️ Sesión #${{idx + 1}} — ${{s.date || ''}}</div>
            <span class="badge badge-info">${{s.sets ? s.sets.length : 0}} series</span>
          </div>
          ${{notesStr}}
          <div class="table-container" style="margin-top: 4px;">
            <table>
              <thead>
                <tr>
                  <th>Ejercicio</th>
                  <th>Serie</th>
                  <th>Reps</th>
                  <th>Peso</th>
                  <th>1RM Est.</th>
                </tr>
              </thead>
              <tbody>
                ${{setsRows}}
              </tbody>
            </table>
          </div>
        `;
        container.appendChild(div);
      }});
    }}

    // Initial fetch of catalogs and summary
    fetchIngredientsList();
    fetchRecipesList();
    fetchExercisesList();
    fetchSummary();
  </script>
</body>
</html>
"""
