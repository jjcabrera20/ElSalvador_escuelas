# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
from pathlib import Path
from html import escape

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="El Salvador",
    page_icon="🏫",
    layout="wide",  # Enable wide mode
    initial_sidebar_state="expanded"
)


# ---------------------------------------------------------
# 0. Language configuration
# ---------------------------------------------------------
TRANSLATIONS = {
    'en': {
        'title': '📍 Schools El Salvador - Interactive Search',
        'subtitle': 'Explore **{:,}** school points with filtering and sorting.',
        'filters': '🎛️ Filters',
        'escuela_codigo': 'School code',
        'domicilio': 'Address',
        'departamento': 'State',
        'municipio': 'Municipality',
        'select_first': 'Select State first',
        'number_schools': '🗺️ **{:,}** schools registered',
        'map_view': '📍 Map View',
        'map_info': 'ℹ️ Displaying {:,} points. Click on a marker to view the code.',
        'data_table': '📊 Data Table',
        'table_subtitle': 'Showing data based on filters. Use search and column sorting to explore.',
        'search_placeholder': '🔍 Search in table (name, locality, etc.)',
        'total_records': '**Total: {:,} records**',
        'found_records': 'Found {:,} matching records',
        'showing_records': 'Showing {:,} of {:,} records',
        'page': 'Page',
        'rows_per_page': 'Rows per page',
        'download_all': '💾 Download All Data',
        'download_filtered': '💾 Download Filtered',
        'download_visible': '💾 Download Current Page',
        'download_disabled_help': 'Use search to filter data first',
        'language': 'Language',
        'name': 'School Name',
        'locality': 'Locality',
        'description': 'Description',
        'click_to_copy': 'Click to view code'
    },
    'es': {
        'title': '📍 Escuelas El Salvador - Consulta Interactiva',
        'subtitle': 'Explora **{:,}** puntos de escuelas con filtrado y ordenamiento.',
        'filters': '🎛️ Filtros',
        'escuela_codigo': 'Código de escuela',
        'domicilio': 'Domicilio',
        'departamento': 'Departamento',
        'municipio': 'Municipio',
        'select_first': 'Selecciona Departamento primero',
        'number_schools': '🗺️ **{:,}** escuelas registradas',
        'map_view': '📍 Vista de Mapa',
        'map_info': 'ℹ️ Mostrando {:,} puntos. Haz clic en un marcador para ver el código.',
        'data_table': '📊 Tabla de Datos',
        'table_subtitle': 'Mostrando datos basados en filtros. Usa búsqueda y ordenamiento de columnas.',
        'search_placeholder': '🔍 Buscar en tabla (nombre, localidad, etc.)',
        'total_records': '**Total: {:,} registros**',
        'found_records': 'Se encontraron {:,} registros coincidentes',
        'showing_records': 'Mostrando {:,} de {:,} registros',
        'page': 'Página',
        'rows_per_page': 'Filas por página',
        'download_all': '💾 Descargar Todo',
        'download_filtered': '💾 Descargar Filtrado',
        'download_visible': '💾 Descargar Página Actual',
        'download_disabled_help': 'Usa búsqueda para filtrar datos primero',
        'language': 'Idioma',
        'name': 'Nombre de Escuela',
        'locality': 'Localidad',
        'description': 'Descripción',
        'click_to_copy': 'Ver código'
    }
}

# Language selector in sidebar
lang = st.sidebar.selectbox(
    "🌐 Language / Idioma",
    options=['en', 'es'],
    format_func=lambda x: 'English' if x == 'en' else 'Español',
    index=1
)
t = TRANSLATIONS[lang]

# ---------------------------------------------------------
# 1. Load and cache data
# ---------------------------------------------------------
@st.cache_data
def load_data():
    path = r'MATRICULA 2024 POR CE_GRADO Y SEXO_DOCENTES_publicar oficial.xlsx'
    try:
        gdf = pd.read_excel(path)
    except Exception as e:
        st.warning(f"⚠️ Could not read excel file directly ({e}), trying fallback...")
    
    return gdf

# ---------------------------------------------------------
# Initialize UI
# ---------------------------------------------------------
gdf = load_data()

st.title(t['title'])
st.markdown(t['subtitle'].format(len(gdf)))

# ---------------------------------------------------------
# 3. Sidebar filters
# ---------------------------------------------------------
st.sidebar.header(t['filters'])

CENTRO_DE_TRABAJO_FIELD = "slv-id"
DEPARTAMENTO_FIELD = "slv-admin1"
MUNICIPIO_FIELD = "slv-admin2"
NOMBRE_DE_CENTRO_DE_TRABAJO = "slv-nombre"
DOMICILIO_COMPLETO = "slv-direccion"

departamentos = sorted(gdf[DEPARTAMENTO_FIELD].dropna().unique().tolist())
admin1 = st.sidebar.selectbox(t['departamento'], departamentos, index=0)

if admin1:
    municipios = [""] + sorted(gdf[gdf[DEPARTAMENTO_FIELD] == admin1][MUNICIPIO_FIELD].dropna().unique().tolist())
    admin2 = st.sidebar.selectbox(t['municipio'], municipios, index=0)

    if admin2:
        filtered_for_map = gdf[
            (gdf[MUNICIPIO_FIELD] == admin2) & (gdf[DEPARTAMENTO_FIELD] == admin1)
        ]
    else:
        filtered_for_map = gdf[gdf[DEPARTAMENTO_FIELD] == admin1]
else:
    filtered_for_map = gdf
    st.sidebar.selectbox(t['municipio'], [t['select_first']], index=0, disabled=True)

st.sidebar.write(t['number_schools'].format(len(filtered_for_map)))

if len(filtered_for_map) > 10000:
    st.sidebar.warning(f"⚠️ {len(filtered_for_map):,} schools. Consider filtering by Municipio for better performance.")
    filtered_for_map = filtered_for_map.head(10000)

# ---------------------------------------------------------
# 5. Data table with pagination
# ---------------------------------------------------------
st.subheader(t['data_table'])
st.markdown(t['table_subtitle'])

table_df = filtered_for_map.copy()

column_display_names = {
    CENTRO_DE_TRABAJO_FIELD: t['escuela_codigo'],
    DEPARTAMENTO_FIELD: t['departamento'],
    MUNICIPIO_FIELD: t['municipio'],
    NOMBRE_DE_CENTRO_DE_TRABAJO: t['name'],
    DOMICILIO_COMPLETO: t['domicilio']
}

display_columns = [
    CENTRO_DE_TRABAJO_FIELD,
    DEPARTAMENTO_FIELD,
    MUNICIPIO_FIELD,
    NOMBRE_DE_CENTRO_DE_TRABAJO,
    DOMICILIO_COMPLETO
]

table_df = table_df[display_columns].copy()
table_df = table_df.rename(columns=column_display_names)

col1, col2 = st.columns([2, 1])
with col1:
    search_term = st.text_input(t['search_placeholder'], "")
with col2:
    st.write("")
    st.write(t['total_records'].format(len(table_df)))

if search_term:
    mask = table_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
    table_df = table_df[mask]
    st.info(t['found_records'].format(len(table_df)))

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    rows_per_page = st.selectbox(
        t['rows_per_page'],
        options=[50, 100, 200, 500],
        index=1
    )
with col2:
    total_pages = max(1, (len(table_df) - 1) // rows_per_page + 1)
    page = st.number_input(
        t['page'],
        min_value=1,
        max_value=total_pages,
        value=1,
        step=1
    )

start_idx = (page - 1) * rows_per_page
end_idx = min(start_idx + rows_per_page, len(table_df))
paginated_df = table_df.iloc[start_idx:end_idx]

st.caption(t['showing_records'].format(len(paginated_df), len(table_df)))

st.dataframe(paginated_df, width='stretch', height=400)

# ---------------------------------------------------------
# Download buttons
# ---------------------------------------------------------
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    csv_filtered = table_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=t['download_all'],
        data=csv_filtered,
        file_name="filtered_schools.csv",
        mime="text/csv",
    )

with col2:
    csv_page = paginated_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=t['download_visible'],
        data=csv_page,
        file_name=f"schools_page_{page}.csv",
        mime="text/csv",
    )
st.write("Fuente/Source: Ministerio de educación de El Salvador (MINED) año 2024")