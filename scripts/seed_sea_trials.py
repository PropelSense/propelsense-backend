"""
Seed script to create sample sea trial data
Run this to populate the database with test data for Meyer Turku vessels
"""
import requests
import json
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api/v1"

# Sample sea trials data for Meyer Turku vessels
sample_trials = [
    {
        "trial_name": "Icon of the Seas - Sea Trial #1",
        "vessel_name": "Icon of the Seas",
        "trial_date": (datetime.now() - timedelta(days=30)).isoformat(),
        "status": "completed",
        "test_location": "Gulf of Finland",
        "duration_hours": 8.5,
        
        # Environmental conditions
        "wind_speed": 12.5,
        "wind_direction": 270,
        "wave_height": 1.2,
        "wave_period": 5.5,
        "water_temperature": 8.5,
        "air_temperature": 6.0,
        "water_depth": 45.0,
        
        # Vessel condition
        "displacement": 250800,
        "draft_fore": 9.2,
        "draft_aft": 9.4,
        "trim": -0.2,
        
        # Predicted performance
        "predicted_speed": 22.5,
        "predicted_power": 45000,
        "predicted_fuel_consumption": 280,
        "predicted_rpm": 145,
        
        # Actual performance
        "actual_speed": 23.1,
        "actual_power": 44200,
        "actual_fuel_consumption": 275,
        "actual_rpm": 143,
        
        # Contract specifications
        "contract_speed": 22.0,
        "contract_power": 48000,
        "contract_fuel": 300,
        
        "notes": "Excellent performance in moderate sea conditions. Vessel exceeded speed expectations while consuming less fuel than predicted."
    },
    {
        "trial_name": "Icon of the Seas - Sea Trial #2",
        "vessel_name": "Icon of the Seas",
        "trial_date": (datetime.now() - timedelta(days=15)).isoformat(),
        "status": "completed",
        "test_location": "Baltic Sea",
        "duration_hours": 12.0,
        
        # Environmental conditions
        "wind_speed": 18.0,
        "wind_direction": 315,
        "wave_height": 2.1,
        "wave_period": 6.8,
        "water_temperature": 7.8,
        "air_temperature": 4.5,
        "water_depth": 52.0,
        
        # Vessel condition
        "displacement": 250800,
        "draft_fore": 9.3,
        "draft_aft": 9.3,
        "trim": 0.0,
        
        # Predicted performance
        "predicted_speed": 21.8,
        "predicted_power": 46500,
        "predicted_fuel_consumption": 295,
        "predicted_rpm": 148,
        
        # Actual performance
        "actual_speed": 21.5,
        "actual_power": 47100,
        "actual_fuel_consumption": 298,
        "actual_rpm": 150,
        
        # Contract specifications
        "contract_speed": 22.0,
        "contract_power": 48000,
        "contract_fuel": 300,
        
        "notes": "Performance within acceptable range despite higher sea state. Minor deviation in speed due to wave resistance."
    },
    {
        "trial_name": "Star of the Seas - Initial Trial",
        "vessel_name": "Star of the Seas",
        "trial_date": (datetime.now() - timedelta(days=45)).isoformat(),
        "status": "completed",
        "test_location": "Gulf of Finland",
        "duration_hours": 10.0,
        
        # Environmental conditions
        "wind_speed": 8.5,
        "wind_direction": 180,
        "wave_height": 0.8,
        "wave_period": 4.2,
        "water_temperature": 10.2,
        "air_temperature": 12.5,
        "water_depth": 48.0,
        
        # Vessel condition
        "displacement": 250800,
        "draft_fore": 9.1,
        "draft_aft": 9.2,
        "trim": -0.1,
        
        # Predicted performance
        "predicted_speed": 23.0,
        "predicted_power": 44800,
        "predicted_fuel_consumption": 278,
        "predicted_rpm": 146,
        
        # Actual performance
        "actual_speed": 23.8,
        "actual_power": 43900,
        "actual_fuel_consumption": 272,
        "actual_rpm": 144,
        
        # Contract specifications
        "contract_speed": 22.0,
        "contract_power": 48000,
        "contract_fuel": 300,
        
        "notes": "Outstanding performance in calm conditions. All parameters significantly better than predicted."
    },
    {
        "trial_name": "Utopia of the Seas - Acceptance Trial",
        "vessel_name": "Utopia of the Seas",
        "trial_date": (datetime.now() - timedelta(days=60)).isoformat(),
        "status": "completed",
        "test_location": "Baltic Sea",
        "duration_hours": 14.5,
        
        # Environmental conditions
        "wind_speed": 15.2,
        "wind_direction": 290,
        "wave_height": 1.8,
        "wave_period": 6.0,
        "water_temperature": 9.1,
        "air_temperature": 8.0,
        "water_depth": 55.0,
        
        # Vessel condition
        "displacement": 236800,
        "draft_fore": 8.9,
        "draft_aft": 9.0,
        "trim": -0.1,
        
        # Predicted performance
        "predicted_speed": 22.2,
        "predicted_power": 43500,
        "predicted_fuel_consumption": 270,
        "predicted_rpm": 142,
        
        # Actual performance
        "actual_speed": 22.0,
        "actual_power": 44100,
        "actual_fuel_consumption": 273,
        "actual_rpm": 144,
        
        # Contract specifications
        "contract_speed": 22.0,
        "contract_power": 46000,
        "contract_fuel": 285,
        
        "notes": "Met all contract specifications. Performance consistent with sister vessels."
    },
    {
        "trial_name": "Future Vessel X - Preliminary Trial",
        "vessel_name": "Future Vessel X",
        "trial_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "status": "planned",
        "test_location": "Gulf of Finland",
        "duration_hours": 8.0,
        
        # Predicted performance (no actuals yet)
        "predicted_speed": 23.5,
        "predicted_power": 46000,
        "predicted_fuel_consumption": 285,
        "predicted_rpm": 147,
        
        # Contract specifications
        "contract_speed": 22.5,
        "contract_power": 48000,
        "contract_fuel": 295,
        
        "notes": "Scheduled for next month. Expected to perform similar to Icon class."
    }
]

def create_trials():
    """Create sample sea trials via API"""
    print("🚢 Creating sample sea trial data...")
    print(f"API endpoint: {API_BASE}/sea-trials\n")
    
    created_count = 0
    for trial in sample_trials:
        try:
            response = requests.post(
                f"{API_BASE}/sea-trials",
                json=trial,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                data = response.json()
                created_count += 1
                print(f"✅ Created: {trial['trial_name']}")
                print(f"   ID: {data['sea_trial_id']}")
                if data.get('overall_performance_score'):
                    print(f"   Performance Score: {data['overall_performance_score']}/100")
                print()
            else:
                print(f"❌ Failed: {trial['trial_name']}")
                print(f"   Status: {response.status_code}")
                print(f"   Error: {response.text}\n")
        
        except Exception as e:
            print(f"❌ Error creating {trial['trial_name']}: {str(e)}\n")
    
    print(f"\n{'='*60}")
    print(f"✨ Created {created_count}/{len(sample_trials)} sea trials")
    print(f"{'='*60}")
    
    # Fetch summary
    try:
        response = requests.get(f"{API_BASE}/sea-trials/summary")
        if response.status_code == 200:
            summary = response.json()
            print(f"\n📊 Summary Statistics:")
            print(f"   Total Trials: {summary['total_trials']}")
            print(f"   Completed: {summary['completed_trials']}")
            print(f"   Avg Performance: {summary['avg_performance_score']}/100" if summary['avg_performance_score'] else "   Avg Performance: N/A")
            print(f"   Meeting Contract: {summary['trials_meeting_contract']}")
    except Exception as e:
        print(f"\n⚠️  Could not fetch summary: {str(e)}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  Meyer Turku Sea Trial Data Seeder")
    print("="*60 + "\n")
    print("⚠️  Make sure the backend server is running on http://localhost:8000\n")
    
    input("Press Enter to continue...")
    
    create_trials()
    
    print("\n🎉 Done! Refresh the Sea Trials dashboard to see the data.\n")
