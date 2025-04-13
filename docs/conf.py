import os
import sys
sys.path.insert(0, os.path.abspath('C:/Users/guvon/Documents/IESB/aprendizagem_maquina/trabalho01_aprendizagem_maquina'))  # Aponta para o diretório pai

project = 'Analisador de Dados'
copyright = '2025, guvon'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx_rtd_theme',
    'sphinx.ext.napoleon',  # Para suportar o formato NumPy/SciPy
    'sphinx.ext.viewcode',
]
html_theme = 'sphinx_rtd_theme'