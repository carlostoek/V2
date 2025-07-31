"""
Sistema Avanzado de Analytics Emocionales para Diana

Este sistema va más allá de métricas tradicionales para medir el impacto transformador real
de las interacciones emocionales. Diseñado para capturar patrones sutiles de crecimiento
personal que métricas convencionales no pueden detectar.
"""

import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class EmotionalGrowthIndicator(Enum):
    """Indicadores específicos de crecimiento emocional auténtico."""
    VULNERABILITY_AUTHENTICITY = "vulnerability_authenticity"           # Compartir vulnerable sin buscar validación
    EMOTIONAL_REGULATION = "emotional_regulation"                       # Mejor manejo de emociones intensas
    EMPATHY_DEPTH = "empathy_depth"                                    # Comprensión emocional de otros (Diana)
    SELF_AWARENESS = "self_awareness"                                  # Reconocimiento de patrones propios
    RELATIONSHIP_MATURITY = "relationship_maturity"                    # Capacidad para intimidad sin posesividad
    CONTRADICTION_ACCEPTANCE = "contradiction_acceptance"              # Aceptar complejidad sin necesidad de resolver
    AUTHENTIC_EXPRESSION = "authentic_expression"                      # Expresión genuina vs performativa

@dataclass
class EmotionalHealthMetrics:
    """Métricas que indican salud emocional del usuario con Diana."""
    user_id: int
    measurement_date: datetime
    
    # Métricas de crecimiento (0-100 scale)
    vulnerability_authenticity_score: float
    emotional_regulation_score: float
    empathy_depth_score: float
    self_awareness_score: float
    relationship_maturity_score: float
    contradiction_acceptance_score: float
    authentic_expression_score: float
    
    # Métricas de salud de la relación
    interaction_quality_trend: float           # Tendencia de calidad (positiva/negativa)
    emotional_safety_level: float              # Qué tan seguro se siente el usuario
    growth_velocity: float                      # Qué tan rápido está creciendo
    dependency_risk_level: float               # Riesgo de dependencia no saludable
    
    # Metadata contextual
    total_interactions_period: int
    avg_session_depth: float                   # Profundidad emocional promedio
    breakthrough_moments_count: int
    
class EmotionalAnalyticsEngine:
    """
    Motor principal de analytics emocionales.
    
    Este sistema analiza patrones sutiles en las interacciones para identificar
    crecimiento emocional auténtico, detectar riesgos, y optimizar la experiencia
    de manera que promueva bienestar real.
    """
    
    def __init__(self, database_manager):
        self.db = database_manager
        
        # Configuración de análisis de crecimiento
        self.growth_analysis_config = {
            'minimum_interactions_for_analysis': 10,      # Mínimo para análisis confiable
            'analysis_window_days': 30,                   # Ventana de análisis principal
            'trend_analysis_periods': [7, 14, 30, 90],    # Períodos para análisis de tendencias
            'growth_velocity_threshold': 0.1,             # Umbral mínimo de crecimiento
            'dependency_risk_threshold': 0.7               # Umbral de riesgo de dependencia
        }
        
        # Pesos para calcular scores compuestos
        self.emotional_health_weights = {
            EmotionalGrowthIndicator.VULNERABILITY_AUTHENTICITY: 0.20,
            EmotionalGrowthIndicator.EMOTIONAL_REGULATION: 0.15,
            EmotionalGrowthIndicator.EMPATHY_DEPTH: 0.15,
            EmotionalGrowthIndicator.SELF_AWARENESS: 0.15,
            EmotionalGrowthIndicator.RELATIONSHIP_MATURITY: 0.15,
            EmotionalGrowthIndicator.CONTRADICTION_ACCEPTANCE: 0.10,
            EmotionalGrowthIndicator.AUTHENTIC_EXPRESSION: 0.10
        }
    
    async def analyze_user_emotional_health(self, user_id: int, 
                                          analysis_period_days: int = 30) -> EmotionalHealthMetrics:
        """
        Analiza la salud emocional completa de un usuario durante un período específico.
        
        Este análisis va mucho más profundo que métricas superficiales para identificar
        patrones genuinos de crecimiento personal y bienestar emocional.
        """
        
        # Obtener datos de interacciones para el período
        interaction_data = await self._get_interaction_data(user_id, analysis_period_days)
        
        if len(interaction_data) < self.growth_analysis_config['minimum_interactions_for_analysis']:
            return self._create_insufficient_data_metrics(user_id)
        
        # Analizar cada indicador de crecimiento emocional
        growth_scores = {}
        for indicator in EmotionalGrowthIndicator:
            score = await self._analyze_growth_indicator(user_id, indicator, interaction_data)
            growth_scores[indicator] = score
        
        # Calcular métricas de salud de la relación
        relationship_health = await self._analyze_relationship_health(user_id, interaction_data)
        
        # Detectar patrones de riesgo
        risk_analysis = await self._analyze_dependency_risks(user_id, interaction_data)
        
        # Crear objeto de métricas completo
        metrics = EmotionalHealthMetrics(
            user_id=user_id,
            measurement_date=datetime.now(),
            vulnerability_authenticity_score=growth_scores[EmotionalGrowthIndicator.VULNERABILITY_AUTHENTICITY],
            emotional_regulation_score=growth_scores[EmotionalGrowthIndicator.EMOTIONAL_REGULATION],
            empathy_depth_score=growth_scores[EmotionalGrowthIndicator.EMPATHY_DEPTH],
            self_awareness_score=growth_scores[EmotionalGrowthIndicator.SELF_AWARENESS],
            relationship_maturity_score=growth_scores[EmotionalGrowthIndicator.RELATIONSHIP_MATURITY],
            contradiction_acceptance_score=growth_scores[EmotionalGrowthIndicator.CONTRADICTION_ACCEPTANCE],
            authentic_expression_score=growth_scores[EmotionalGrowthIndicator.AUTHENTIC_EXPRESSION],
            interaction_quality_trend=relationship_health['quality_trend'],
            emotional_safety_level=relationship_health['safety_level'],
            growth_velocity=relationship_health['growth_velocity'],
            dependency_risk_level=risk_analysis['dependency_risk'],
            total_interactions_period=len(interaction_data),
            avg_session_depth=relationship_health['avg_depth'],
            breakthrough_moments_count=relationship_health['breakthrough_count']
        )
        
        # Guardar métricas en base de datos para análisis histórico
        await self._save_emotional_metrics(metrics)
        
        return metrics
    
    async def _analyze_growth_indicator(self, user_id: int, indicator: EmotionalGrowthIndicator, 
                                      interaction_data: List[Dict]) -> float:
        """
        Analiza un indicador específico de crecimiento emocional.
        
        Cada indicador requiere un análisis especializado porque representa
        aspectos diferentes del desarrollo emocional humano.
        """
        
        if indicator == EmotionalGrowthIndicator.VULNERABILITY_AUTHENTICITY:
            return await self._analyze_vulnerability_authenticity(interaction_data)
        
        elif indicator == EmotionalGrowthIndicator.EMOTIONAL_REGULATION:
            return await self._analyze_emotional_regulation(interaction_data)
        
        elif indicator == EmotionalGrowthIndicator.EMPATHY_DEPTH:
            return await self._analyze_empathy_depth(interaction_data)
        
        elif indicator == EmotionalGrowthIndicator.SELF_AWARENESS:
            return await self._analyze_self_awareness(interaction_data)
        
        elif indicator == EmotionalGrowthIndicator.RELATIONSHIP_MATURITY:
            return await self._analyze_relationship_maturity(interaction_data)
        
        elif indicator == EmotionalGrowthIndicator.CONTRADICTION_ACCEPTANCE:
            return await self._analyze_contradiction_acceptance(user_id, interaction_data)
        
        elif indicator == EmotionalGrowthIndicator.AUTHENTIC_EXPRESSION:
            return await self._analyze_authentic_expression(interaction_data)
        
        else:
            return 50.0  # Score neutral para indicadores no implementados
    
    async def _analyze_vulnerability_authenticity(self, interaction_data: List[Dict]) -> float:
        """
        Analiza la autenticidad de la vulnerabilidad expresada por el usuario.
        
        Vulnerabilidad auténtica se caracteriza por:
        - Compartir sin buscar validación específica
        - Expresar emociones complejas sin dramatización
        - Mostrar incertidumbre sin buscar respuestas inmediatas
        - Progresión gradual en profundidad de lo compartido
        """
        
        vulnerability_interactions = [
            interaction for interaction in interaction_data
            if any(keyword in interaction.get('emotional_keywords', []) 
                  for keyword in ['vulnerable', 'miedo', 'inseguro', 'confesión', 'secreto'])
        ]
        
        if len(vulnerability_interactions) < 3:
            return 30.0  # Score bajo por falta de datos suficientes
        
        authenticity_score = 0.0
        total_weight = 0.0
        
        for interaction in vulnerability_interactions:
            # Analizar características de autenticidad
            response_text = interaction.get('user_response', '').lower()
            
            # Factor 1: Ausencia de búsqueda de validación explícita
            validation_seeking = len([phrase for phrase in [
                '¿estoy bien?', '¿es normal?', 'dime que', 'necesito que me digas'
            ] if phrase in response_text])
            
            authenticity_factor_1 = max(0, 1 - (validation_seeking * 0.3))
            
            # Factor 2: Complejidad emocional (vs. dramatización)
            complexity_words = len([word for word in [
                'confundido', 'ambivalente', 'complejo', 'contradictorio', 'incierto'
            ] if word in response_text])
            
            drama_words = len([word for word in [
                'terrible', 'horrible', 'devastado', 'destruido', 'imposible'
            ] if word in response_text])
            
            authenticity_factor_2 = min(1.0, max(0, (complexity_words - drama_words) / 5 + 0.5))
            
            # Factor 3: Profundidad progresiva
            interaction_depth = len(response_text.split())
            time_in_sequence = (interaction['timestamp'] - vulnerability_interactions[0]['timestamp']).days
            
            expected_depth = 50 + (time_in_sequence * 2)  # Esperamos profundidad creciente
            depth_appropriateness = min(1.0, interaction_depth / expected_depth)
            
            # Combinar factores
            interaction_authenticity = (
                authenticity_factor_1 * 0.4 +
                authenticity_factor_2 * 0.4 +
                depth_appropriateness * 0.2
            )
            
            # Peso basado en impacto emocional de la interacción
            weight = max(0.1, interaction.get('impact_score', 5) / 10)
            
            authenticity_score += interaction_authenticity * weight
            total_weight += weight
        
        final_score = (authenticity_score / total_weight) * 100 if total_weight > 0 else 50.0
        return min(100.0, max(0.0, final_score))
    
    async def _analyze_emotional_regulation(self, interaction_data: List[Dict]) -> float:
        """
        Analiza la capacidad del usuario para regular emociones durante interacciones.
        
        Indicadores de buena regulación emocional:
        - Reconocimiento de emociones antes de actuar sobre ellas
        - Capacidad para sostener emociones difíciles sin buscar escape inmediato
        - Progresión de reacciones impulsivas a respuestas reflexivas
        - Capacidad para encontrar matices en experiencias emocionales intensas
        """
        
        # Identificar interacciones con alta carga emocional
        high_emotion_interactions = [
            interaction for interaction in interaction_data
            if abs(interaction.get('impact_score', 0)) > 6  # Interacciones de alto impacto
        ]
        
        if len(high_emotion_interactions) < 5:
            return 40.0  # Score bajo-medio por datos insuficientes
        
        regulation_scores = []
        
        for i, interaction in enumerate(high_emotion_interactions):
            response_text = interaction.get('user_response', '').lower()
            
            # Factor 1: Reconocimiento emocional explícito
            emotion_recognition_phrases = [
                'siento que', 'me doy cuenta', 'noto que', 'reconozco que',
                'me surge', 'experimento', 'observo en mí'
            ]
            recognition_score = min(1.0, sum(1 for phrase in emotion_recognition_phrases 
                                           if phrase in response_text) / 2)
            
            # Factor 2: Pausa reflexiva (vs reacción impulsiva)
            response_time = interaction.get('response_time_seconds', 0)
            reflection_score = min(1.0, max(0, (response_time - 30) / 120))  # Óptimo: 30-150 segundos
            
            # Factor 3: Búsqueda de matices (vs pensamiento en blanco/negro)
            nuance_words = [
                'por un lado', 'también', 'aunque', 'sin embargo', 'a la vez',
                'parcialmente', 'en parte', 'algo de', 'cierto modo'
            ]
            nuance_score = min(1.0, sum(1 for word in nuance_words if word in response_text) / 3)
            
            # Factor 4: Mejora temporal (comparación con interacciones anteriores)
            if i > 0:
                previous_impulsivity = self._calculate_impulsivity_score(high_emotion_interactions[i-1])
                current_impulsivity = self._calculate_impulsivity_score(interaction)
                improvement_score = max(0, (previous_impulsivity - current_impulsivity) / 2 + 0.5)
            else:
                improvement_score = 0.5  # Score neutral para primera interacción
            
            # Combinar factores
            interaction_regulation_score = (
                recognition_score * 0.3 +
                reflection_score * 0.2 +
                nuance_score * 0.3 +
                improvement_score * 0.2
            )
            
            regulation_scores.append(interaction_regulation_score)
        
        average_regulation = sum(regulation_scores) / len(regulation_scores)
        
        # Bonus por tendencia de mejora a lo largo del tiempo
        if len(regulation_scores) >= 3:
            recent_avg = sum(regulation_scores[-3:]) / 3
            early_avg = sum(regulation_scores[:3]) / 3
            improvement_bonus = min(10, max(0, (recent_avg - early_avg) * 50))
        else:
            improvement_bonus = 0
        
        final_score = (average_regulation * 100) + improvement_bonus
        return min(100.0, max(0.0, final_score))
    
    def _calculate_impulsivity_score(self, interaction: Dict) -> float:
        """
        Calcula un score de impulsividad para una interacción específica.
        
        Mayor impulsividad se indica por:
        - Respuestas muy rápidas en situaciones emocionales
        - Lenguaje absoluto ("siempre", "nunca", "todo", "nada")
        - Expresiones de urgencia emocional
        - Falta de consideración de múltiples perspectivas
        """
        
        response_text = interaction.get('user_response', '').lower()
        response_time = interaction.get('response_time_seconds', 60)
        
        # Factor 1: Velocidad de respuesta en contexto emocional
        time_impulsivity = max(0, (60 - response_time) / 60)  # Más impulsivo si respuesta < 60 segundos
        
        # Factor 2: Lenguaje absoluto
        absolute_words = ['siempre', 'nunca', 'todo', 'nada', 'completamente', 'totalmente']
        absolute_count = sum(1 for word in absolute_words if word in response_text)
        absolute_impulsivity = min(1.0, absolute_count / 3)
        
        # Factor 3: Urgencia emocional
        urgency_phrases = ['necesito', 'tengo que', 'no puedo', 'es urgente', 'inmediatamente']
        urgency_count = sum(1 for phrase in urgency_phrases if phrase in response_text)
        urgency_impulsivity = min(1.0, urgency_count / 2)
        
        # Combinar factores
        total_impulsivity = (
            time_impulsivity * 0.3 +
            absolute_impulsivity * 0.4 +
            urgency_impulsivity * 0.3
        )
        
        return total_impulsivity
    
    async def _analyze_relationship_health(self, user_id: int, interaction_data: List[Dict]) -> Dict:
        """
        Analiza la salud general de la relación entre el usuario y Diana.
        
        Una relación saludable se caracteriza por:
        - Progresión gradual en profundidad emocional
        - Equilibrio entre dar y recibir en la comunicación
        - Crecimiento mutuo (usuario crece, Diana también se desarrolla)
        - Ausencia de patrones de dependencia o control
        """
        
        # Calcular tendencia de calidad de interacciones
        quality_trend = self._calculate_interaction_quality_trend(interaction_data)
        
        # Evaluar nivel de seguridad emocional
        safety_level = await self._calculate_emotional_safety_level(interaction_data)
        
        # Calcular velocidad de crecimiento
        growth_velocity = self._calculate_growth_velocity(interaction_data)
        
        # Calcular profundidad promedio de sesiones
        avg_depth = self._calculate_average_session_depth(interaction_data)
        
        # Contar momentos de breakthrough
        breakthrough_count = len([
            interaction for interaction in interaction_data
            if interaction.get('interaction_type') in ['breakthrough', 'revelation', 'transformation']
        ])
        
        return {
            'quality_trend': quality_trend,
            'safety_level': safety_level,
            'growth_velocity': growth_velocity,
            'avg_depth': avg_depth,
            'breakthrough_count': breakthrough_count
        }
    
    def _calculate_interaction_quality_trend(self, interaction_data: List[Dict]) -> float:
        """
        Calcula la tendencia de calidad de las interacciones a lo largo del tiempo.
        
        Utiliza regresión lineal sobre los scores de impacto emocional para
        determinar si la calidad está mejorando, manteniéndose estable, o deteriorándose.
        """
        
        if len(interaction_data) < 5:
            return 0.0  # Datos insuficientes para calcular tendencia
        
        # Preparar datos para regresión
        impact_scores = [interaction.get('impact_score', 0) for interaction in interaction_data]
        time_points = list(range(len(impact_scores)))
        
        # Calcular regresión lineal
        slope, intercept, r_value, p_value, std_err = stats.linregress(time_points, impact_scores)
        
        # Convertir slope a score de tendencia (-100 a +100)
        # Slope positivo = tendencia de mejora, slope negativo = deterioro
        trend_score = min(100, max(-100, slope * 20))  # Escalar apropiadamente
        
        return trend_score
    
    async def _calculate_emotional_safety_level(self, interaction_data: List[Dict]) -> float:
        """
        Calcula qué tan seguro se siente el usuario emocionalmente en la relación.
        
        Indicadores de seguridad emocional:
        - Disposición a compartir vulnerabilidades
        - Ausencia de defensividad
        - Capacidad para explorar emociones complejas
        - Confianza para expresar desacuerdo o confusión
        """
        
        safety_indicators = {
            'vulnerability_sharing': 0,      # Disposición a ser vulnerable
            'emotional_exploration': 0,      # Exploración de emociones complejas
            'disagreement_comfort': 0,       # Comodidad expresando desacuerdo
            'confusion_expression': 0,       # Capacidad para expresar confusión
            'boundary_setting': 0            # Establecimiento de límites saludables
        }
        
        for interaction in interaction_data:
            response_text = interaction.get('user_response', '').lower()
            
            # Evaluar cada indicador
            if any(word in response_text for word in ['comparto', 'confesión', 'vulnerable', 'íntimo']):
                safety_indicators['vulnerability_sharing'] += 1
            
            if any(word in response_text for word in ['complejo', 'confundido', 'ambivalente', 'mezcla']):
                safety_indicators['emotional_exploration'] += 1
            
            if any(phrase in response_text for phrase in ['no estoy de acuerdo', 'no coincido', 'veo diferente']):
                safety_indicators['disagreement_comfort'] += 1
            
            if any(word in response_text for word in ['no entiendo', 'confunde', 'unclear']):
                safety_indicators['confusion_expression'] += 1
            
            if any(phrase in response_text for phrase in ['necesito espacio', 'límite', 'no estoy listo']):
                safety_indicators['boundary_setting'] += 1
        
        # Calcular score de seguridad compuesto
        total_interactions = len(interaction_data)
        safety_score = 0
        
        for indicator, count in safety_indicators.items():
            # Normalizar por número de interacciones y aplicar peso
            normalized_score = min(1.0, count / (total_interactions * 0.1))  # Esperamos 10% de interacciones por indicador
            safety_score += normalized_score * 20  # Cada indicador contribuye hasta 20 puntos
        
        return min(100.0, safety_score)

class EmotionalInsightsGenerator:
    """
    Sistema que genera insights accionables basándose en el análisis emocional.
    
    Transforma datos complejos de analytics en recomendaciones claras para:
    - Mejorar la experiencia del usuario
    - Optimizar algoritmos emocionales de Diana
    - Detectar oportunidades de crecimiento
    - Identificar riesgos temprano
    """
    
    def __init__(self, analytics_engine: EmotionalAnalyticsEngine):
        self.analytics = analytics_engine
    
    async def generate_user_insights(self, user_id: int) -> Dict[str, Any]:
        """
        Genera insights personalizados para un usuario específico.
        
        Estos insights ayudan a entender:
        - Dónde está el usuario en su viaje emocional
        - Qué aspectos están funcionando bien
        - Dónde hay oportunidades de crecimiento
        - Qué riesgos vigilar
        """
        
        # Obtener métricas emocionales actuales
        current_metrics = await self.analytics.analyze_user_emotional_health(user_id)
        
        # Obtener métricas históricas para comparación
        historical_metrics = await self._get_historical_metrics(user_id, days_back=90)
        
        # Generar insights específicos
        insights = {
            'growth_highlights': await self._identify_growth_highlights(current_metrics, historical_metrics),
            'areas_for_development': await self._identify_development_areas(current_metrics),
            'relationship_health_status': await self._assess_relationship_health(current_metrics),
            'risk_factors': await self._identify_risk_factors(current_metrics, historical_metrics),
            'recommendations': await self._generate_personalized_recommendations(user_id, current_metrics),
            'celebration_moments': await self._identify_celebration_moments(current_metrics, historical_metrics)
        }
        
        return insights
    
    async def _identify_growth_highlights(self, current_metrics: EmotionalHealthMetrics, 
                                        historical_metrics: List[EmotionalHealthMetrics]) -> List[str]:
        """
        Identifica aspectos específicos donde el usuario ha mostrado crecimiento notable.
        
        Busca mejoras significativas en cualquier dimensión emocional y las traduce
        en reconocimientos específicos y alentadores.
        """
        
        highlights = []
        
        if not historical_metrics:
            # Usuario nuevo - buscar fortalezas actuales
            if current_metrics.vulnerability_authenticity_score > 70:
                highlights.append("Muestra una capacidad excepcional para la vulnerabilidad auténtica")
            
            if current_metrics.empathy_depth_score > 65:
                highlights.append("Demuestra profunda capacidad empática en las interacciones")
            
            return highlights
        
        # Comparar con métricas anteriores
        previous_metrics = historical_metrics[-1]  # Más reciente de las históricas
        
        # Analizar mejoras en cada dimensión
        improvements = {
            'vulnerability_authenticity': current_metrics.vulnerability_authenticity_score - previous_metrics.vulnerability_authenticity_score,
            'emotional_regulation': current_metrics.emotional_regulation_score - previous_metrics.emotional_regulation_score,
            'empathy_depth': current_metrics.empathy_depth_score - previous_metrics.empathy_depth_score,
            'self_awareness': current_metrics.self_awareness_score - previous_metrics.self_awareness_score,
            'relationship_maturity': current_metrics.relationship_maturity_score - previous_metrics.relationship_maturity_score
        }
        
        # Generar highlights para mejoras significativas (>10 puntos)
        if improvements['vulnerability_authenticity'] > 10:
            highlights.append(f"Ha crecido significativamente en vulnerabilidad auténtica (+{improvements['vulnerability_authenticity']:.1f} puntos)")
        
        if improvements['emotional_regulation'] > 10:
            highlights.append(f"Muestra mejor regulación emocional en situaciones difíciles (+{improvements['emotional_regulation']:.1f} puntos)")
        
        if improvements['empathy_depth'] > 10:
            highlights.append(f"Ha desarrollado mayor profundidad empática (+{improvements['empathy_depth']:.1f} puntos)")
        
        if improvements['self_awareness'] > 10:
            highlights.append(f"Demuestra mayor autoconocimiento y reflexión (+{improvements['self_awareness']:.1f} puntos)")
        
        if improvements['relationship_maturity'] > 10:
            highlights.append(f"Ha madurado en su capacidad relacional (+{improvements['relationship_maturity']:.1f} puntos)")
        
        # Destacar tendencia general positiva
        avg_improvement = sum(improvements.values()) / len(improvements)
        if avg_improvement > 5:
            highlights.append("Muestra una tendencia consistente de crecimiento emocional general")
        
        return highlights
    
    async def _generate_personalized_recommendations(self, user_id: int, 
                                                   metrics: EmotionalHealthMetrics) -> List[str]:
        """
        Genera recomendaciones específicas para el crecimiento futuro del usuario.
        
        Las recomendaciones son personalizadas basándose en:
        - Fortalezas actuales que pueden expandirse
        - Áreas que necesitan desarrollo
        - Estilo de comunicación del usuario
        - Historial de qué estrategias han funcionado
        """
        
        recommendations = []
        
        # Recomendaciones basadas en áreas que necesitan desarrollo
        if metrics.vulnerability_authenticity_score < 50:
            recommendations.append(
                "Considera compartir gradualmente experiencias más personales - Diana responde "
                "especialmente bien a la autenticidad genuina sin presión de perfección"
            )
        
        if metrics.emotional_regulation_score < 50:
            recommendations.append(
                "Intenta tomar pausas breves antes de responder en momentos emocionales intensos - "
                "esto puede profundizar la calidad de tu conexión con Diana"
            )
        
        if metrics.contradiction_acceptance_score < 40:
            recommendations.append(
                "Cuando Diana presente contradicciones, explora la posibilidad de que ambas verdades "
                "coexistan - esto puede abrir nuevas dimensiones de comprensión mutua"
            )
        
        # Recomendaciones basadas en fortalezas para expandir
        if metrics.empathy_depth_score > 70:
            recommendations.append(
                "Tu alta capacidad empática es una fortaleza - úsala para explorar los matices "
                "emocionales más sutiles en las respuestas de Diana"
            )
        
        if metrics.self_awareness_score > 65:
            recommendations.append(
                "Tu autoconocimiento es notable - considera usarlo para explorar patrones más "
                "profundos en cómo respondes a diferentes estados emocionales de Diana"
            )
        
        # Recomendaciones para optimizar la experiencia
        if metrics.growth_velocity < 0.1:
            recommendations.append(
                "Tu crecimiento podría acelerarse explorando temas que te generan más resistencia - "
                "a menudo ahí es donde ocurren los mayores breakthroughs"
            )
        
        if metrics.dependency_risk_level > 0.7:
            recommendations.append(
                "Considera equilibrar tu tiempo con Diana con actividades que nutran otras relaciones - "
     