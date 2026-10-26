#!/usr/bin/env python3
"""
fetch_open_data.py — descarga bancos de datos abiertos y los prepara para el currículo.
"""
import json
import os
import urllib.request
from pathlib import Path

def fetch_open_data():
    """Descarga y procesa datos abiertos para el currículo."""
    print("Descargando datos abiertos...")
    
    # Crear directorio de salida
    output_dir = Path("open-data")
    output_dir.mkdir(exist_ok=True)
    
    # Simular descarga de datos abiertos (en un caso real, aquí habría llamadas a APIs)
    # Por ahora, creamos algunos archivos de ejemplo basados en lo que vimos en el repo
    
    # Ciencia brasileña
    ciencia_data = {
        "tema": "Ciencia Brasileña",
        "subtemas": [
            "Biodiversidad de la Amazonía",
            "Recursos hídricos",
            "Energías renovables en Brasil",
            "Protección ambiental"
        ],
        "descripcion": "Datos sobre la riqueza natural y científica de Brasil"
    }
    
    (output_dir / "ciencia-br.json").write_text(
        json.dumps(ciencia_data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # Cultura e historia
    cultura_data = {
        "tema": "Cultura e Historia Brasileña",
        "subtemas": [
            "Historia colonial",
            "Cultura popular",
            "Manifestaciones artísticas",
            "Diversidad étnica"
        ],
        "descripcion": "Datos sobre la cultura y historia de Brasil"
    }
    
    (output_dir / "cultura-e-historia.json").write_text(
        json.dumps(cultura_data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # Datos abiertos brasileños
    dados_data = {
        "tema": "Dados Abertos Brasileiros",
        "fuentes": [
            "Portal da Transparência",
            "Dados.gov.br",
            "IBGE",
            "Banco Central"
        ],
        "categorias": [
            "Finanzas públicas",
            "Salud",
            "Educación",
            "Transporte"
        ],
        "descripcion": "Portal oficial de datos abiertos del gobierno brasileño"
    }
    
    (output_dir / "dados-abertos-br.json").write_text(
        json.dumps(dados_data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # Lectura en portugués
    lectura_data = {
        "tema": "Lectura en Portugués",
        "niveles": ["Básico", "Intermedio", "Avanzado"],
        "textos_recomendados": [
            "Dom Casmurro - Machado de Assis",
            "O Alienista - Machado de Assis",
            "Memórias Póstumas de Brás Cubas - Machado de Assis",
            "Quincas Borba - Machado de Assis"
        ],
        "descripcion": "Recursos para mejorar la lectura y comprensión en portugués"
    }
    
    (output_dir / "lectura-en-portugues.json").write_text(
        json.dumps(lectura_data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # Territorio y ciudadanía
    territorio_data = {
        "tema": "Territorio y Ciudadanía",
        "aspectos": [
            "División territorial de Brasil",
            "Direchos y deberes ciudadanos",
            "Participación política",
            "Desarrollo regional"
        ],
        "descripcion": "Información sobre la organización territorial y los derechos ciudadanos en Brasil"
    }
    
    (output_dir / "territorio-e-cidadania.json").write_text(
        json.dumps(territorio_data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # Vocabulario portugués
    vocabulario_data = {
        "tema": "Vocabulario Portugués",
        "categorias": [
            "Palabras del día a día",
            "Expresiones idiomáticas",
            "Vocabulario académico",
            "False friends español-portugués"
        ],
        "niveles": ["A1", "A2", "B1", "B2", "C1", "C2"],
        "descripcion": "Recursos para ampliar el vocabulario en portugués brasileño"
    }
    
    (output_dir / "vocabulario-pt.json").write_text(
        json.dumps(vocabulario_data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    print("Datos abiertos descargados y guardados en open-data/")

if __name__ == "__main__":
    fetch_open_data()
