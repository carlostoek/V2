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
