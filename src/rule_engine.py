"""
Rule Engine Module
Converts numeric values into categories before AI processing
"""

from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class HealthCategories:
    """Stores categorized health metrics"""
    bmi_category: str
    visceral_fat_category: str
    body_fat_category: str
    muscle_mass_category: str
    body_age_status: str
    overall_risk_level: str


class RuleEngine:
    """Processes health metrics and converts them to categories"""
    
    @staticmethod
    def categorize_bmi(bmi: float) -> str:
        """Categorize BMI value (10-50 valid range)"""
        if bmi < 18:
            return "Underweight"
        elif 18 <= bmi < 23:
            return "Normal Weight"
        elif 23 <= bmi < 25:
            return "Overweight"
        elif 25 <= bmi < 30:
            return "Obesity Grade 1"
        else:
            return "High Obesity Risk"
    
    @staticmethod
    def categorize_visceral_fat(vf: float) -> str:
        """Categorize Visceral Fat (1-30 valid range)"""
        if 1 <= vf <= 8:
            return "Normal"
        elif 9 <= vf <= 14:
            return "High"
        else:
            return "Very High Risk"
    
    @staticmethod
    def categorize_body_fat(body_fat: float, gender: str) -> str:
        """Categorize Body Fat % based on gender"""
        if gender.lower() == "male":
            if body_fat < 14:
                return "Low (Lean)"
            elif 14 <= body_fat <= 17:
                return "Normal"
            elif 18 <= body_fat <= 24:
                return "Moderate"
            else:
                return "High Risk"
        else:  # Female
            if body_fat < 21:
                return "Low (Lean)"
            elif 21 <= body_fat <= 24:
                return "Normal"
            elif 25 <= body_fat <= 34:
                return "Moderate"
            else:
                return "High Risk"
    
    @staticmethod
    def categorize_muscle_mass(muscle_mass: float, gender: str) -> str:
        """Categorize Muscle Mass % based on gender"""
        if gender.lower() == "male":
            if muscle_mass < 30:
                return "Low"
            elif 30 <= muscle_mass <= 40:
                return "Normal"
            else:
                return "High (Athletic)"
        else:  # Female
            if muscle_mass < 20:
                return "Low"
            elif 20 <= muscle_mass <= 30:
                return "Normal"
            else:
                return "High (Athletic)"
    
    @staticmethod
    def evaluate_body_age(body_age: int, actual_age: int) -> Tuple[str, str]:
        """
        Evaluate body age vs actual age
        Returns: (status, risk_indicator)
        """
        difference = body_age - actual_age
        
        if difference <= -5:
            return "Excellent (5+ years younger)", "✅ Very Good"
        elif -5 < difference < 0:
            return "Good (younger than actual age)", "✅ Good"
        elif difference == 0:
            return "Matched with actual age", "⚠️ Neutral"
        elif 0 < difference <= 5:
            return "Slightly elevated (up to 5 years older)", "⚠️ Minor Concern"
        else:
            return "Significantly elevated (5+ years older)", "❌ Risk"
    
    @staticmethod
    def calculate_overall_risk(categories: HealthCategories) -> str:
        """Calculate overall risk level based on all categories"""
        risk_indicators = 0
        
        # BMI risk
        if "Obesity" in categories.bmi_category or "Overweight" in categories.bmi_category:
            risk_indicators += 1
        
        # Visceral Fat risk
        if "High" in categories.visceral_fat_category or "Very High" in categories.visceral_fat_category:
            risk_indicators += 1
        
        # Body Fat risk
        if "High Risk" in categories.body_fat_category:
            risk_indicators += 1
        
        # Muscle Mass risk
        if "Low" in categories.muscle_mass_category:
            risk_indicators += 1
        
        # Body Age risk
        if "Risk" in categories.body_age_status:
            risk_indicators += 1
        
        # Determine overall risk level
        if risk_indicators == 0:
            return "Low Risk"
        elif risk_indicators <= 2:
            return "Moderate Risk"
        elif risk_indicators <= 3:
            return "High Risk"
        else:
            return "Very High Risk"
    
    @staticmethod
    def process_health_metrics(health_data: Dict, patient_age: int, gender: str) -> Dict:
        """
        Process health metrics and generate categories
        Returns dictionary with categorized values
        """
        try:
            # Extract metrics (optional ones may be None = not detected by machine)
            weight       = health_data.get("weight", 0)
            bmi          = health_data.get("bmi", 0)
            bmr          = health_data.get("bmr")          # may be None
            body_fat     = health_data.get("body_fat")     # may be None
            visceral_fat = health_data.get("visceral_fat") # may be None
            body_age     = health_data.get("body_age")     # may be None
            tsf          = health_data.get("tsf")          # may be None
            muscle_mass  = health_data.get("muscle_mass")  # may be None

            # Categorise — use "Not Measured" when the machine didn't detect the value
            bmi_category = RuleEngine.categorize_bmi(bmi)
            vf_category  = (RuleEngine.categorize_visceral_fat(visceral_fat)
                            if visceral_fat is not None else "Not Measured")
            bf_category  = (RuleEngine.categorize_body_fat(body_fat, gender)
                            if body_fat is not None else "Not Measured")
            mm_category  = (RuleEngine.categorize_muscle_mass(muscle_mass, gender)
                            if muscle_mass is not None else "Not Measured")
            ba_status, _ = (RuleEngine.evaluate_body_age(body_age, patient_age)
                            if body_age is not None else ("Not Measured", "—"))
            
            # Create categories object
            categories = HealthCategories(
                bmi_category=bmi_category,
                visceral_fat_category=vf_category,
                body_fat_category=bf_category,
                muscle_mass_category=mm_category,
                body_age_status=ba_status,
                overall_risk_level=""
            )
            
            # Calculate overall risk
            overall_risk = RuleEngine.calculate_overall_risk(categories)
            categories.overall_risk_level = overall_risk
            
            # Generate wellness score (0-10 scale, higher is worse)
            wellness_score = RuleEngine.calculate_wellness_score(categories)
            
            # Generate summary
            summary = RuleEngine.generate_health_summary(
                categories, weight, bmi, body_fat, visceral_fat, 
                muscle_mass, body_age, patient_age, gender
            )
            
            return {
                "bmi_category": bmi_category,
                "visceral_fat_category": vf_category,
                "body_fat_category": bf_category,
                "muscle_mass_category": mm_category,
                "body_age_status": ba_status,
                "overall_risk_level": overall_risk,
                "wellness_score": wellness_score,
                "health_summary": summary
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "bmi_category": "Error",
                "visceral_fat_category": "Error",
                "body_fat_category": "Error",
                "muscle_mass_category": "Error",
                "body_age_status": "Error",
                "overall_risk_level": "Unable to calculate",
                "wellness_score": 0,
                "health_summary": ""
            }
    
    @staticmethod
    def calculate_wellness_score(categories: HealthCategories) -> float:
        """
        Calculate wellness score (0-10)
        0 = Perfect health, 10 = Critical risk
        """
        score = 5.0  # Base score
        
        # Adjust based on BMI
        if "Underweight" in categories.bmi_category:
            score -= 0.5
        elif "Normal" in categories.bmi_category:
            score -= 0.5
        elif "Overweight" in categories.bmi_category:
            score += 1.0
        elif "Grade 1" in categories.bmi_category:
            score += 2.0
        elif "High Obesity" in categories.bmi_category:
            score += 3.0
        
        # Adjust based on Visceral Fat
        if "Normal" in categories.visceral_fat_category:
            score -= 0.5
        elif "High" in categories.visceral_fat_category:
            score += 1.5
        elif "Very High" in categories.visceral_fat_category:
            score += 2.5
        
        # Adjust based on Body Fat
        if "Low" in categories.body_fat_category or "Normal" in categories.body_fat_category:
            score -= 0.5
        elif "Moderate" in categories.body_fat_category:
            score += 1.0
        elif "High Risk" in categories.body_fat_category:
            score += 2.0
        
        # Adjust based on Muscle Mass
        if "Low" in categories.muscle_mass_category:
            score += 1.5
        elif "High" in categories.muscle_mass_category:
            score -= 1.0
        
        # Clamp score between 0 and 10
        return max(0, min(10, round(score, 1)))
    
    @staticmethod
    def generate_health_summary(categories: HealthCategories, weight: float, bmi: float, 
                               body_fat, visceral_fat, muscle_mass,
                               body_age, actual_age: int, gender: str) -> str:
        """Generate a structured health summary for AI processing.
        Optional fields (body_fat, visceral_fat, muscle_mass, body_age) may be None
        when the machine could not detect them (e.g. elderly patients).
        """
        
        summary_parts = []
        
        # Basic metrics
        summary_parts.append(f"Patient Profile: {gender}, Age: {actual_age}")
        summary_parts.append(f"\nPhysical Measurements:")
        summary_parts.append(f"- Weight: {weight} kg")
        summary_parts.append(f"- BMI: {bmi} ({categories.bmi_category})")
        
        # Body composition
        summary_parts.append(f"\nBody Composition:")
        if body_fat is not None:
            summary_parts.append(f"- Body Fat: {body_fat}% ({categories.body_fat_category})")
        else:
            summary_parts.append("- Body Fat: Not measured by machine")
        if visceral_fat is not None:
            summary_parts.append(f"- Visceral Fat: {visceral_fat} ({categories.visceral_fat_category})")
        else:
            summary_parts.append("- Visceral Fat: Not measured by machine")
        if muscle_mass is not None:
            summary_parts.append(f"- Muscle Mass: {muscle_mass}% ({categories.muscle_mass_category})")
        else:
            summary_parts.append("- Muscle Mass: Not measured by machine")
        
        # Body age analysis
        summary_parts.append(f"\nAge Analysis:")
        summary_parts.append(f"- Actual Age: {actual_age} years")
        if body_age is not None:
            summary_parts.append(f"- Body Age: {body_age} years")
            summary_parts.append(f"- Status: {categories.body_age_status}")
        else:
            summary_parts.append("- Body Age: Not measured by machine")
        
        # Risk assessment
        summary_parts.append(f"\nOverall Risk Assessment: {categories.overall_risk_level}")
        
        # Key findings (only for measured values)
        summary_parts.append(f"\nKey Health Findings:")
        if "Overweight" in categories.bmi_category or "Obesity" in categories.bmi_category:
            summary_parts.append("- Weight management is a priority")
        if visceral_fat is not None and ("High" in categories.visceral_fat_category or "Very High" in categories.visceral_fat_category):
            summary_parts.append("- Visceral fat levels are elevated and require attention")
        if muscle_mass is not None and "Low" in categories.muscle_mass_category:
            summary_parts.append("- Muscle mass is below optimal range")
        if body_age is not None and body_age > actual_age + 5:
            summary_parts.append("- Body age indicates accelerated aging; lifestyle modifications needed")
        
        return "\n".join(summary_parts)
