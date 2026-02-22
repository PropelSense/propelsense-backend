"""
Seed script – Meyer Turku sea trial data
Run with the backend server already running:
    python scripts/seed_sea_trials.py

Updated fields (v2):
  - time_since_dry_dock  : days since last dry dock (ML feature)
  - current_speed / current_direction : now present on every completed trial
  - trim removed from payload (stored, but calculated as draft_aft - draft_fore
    by the client/user; the API accepts it but it is not required)
"""
import sys
import requests
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api/v1"


# ---------------------------------------------------------------------------
# Sample data
# Each completed trial has all fields required for the ⚡ ML Predict button:
#   actual_speed, draft_fore, draft_aft, wind_speed/direction,
#   current_speed/direction, wave_height, time_since_dry_dock
# ---------------------------------------------------------------------------
sample_trials = [
    # ------------------------------------------------------------------
    # Icon of the Seas
    # ------------------------------------------------------------------
    {
        "trial_name": "Icon of the Seas – Sea Trial #1",
        "vessel_name": "Icon of the Seas",
        "trial_date": (datetime.now() - timedelta(days=30)).isoformat(),
        "status": "completed",
        "test_location": "Gulf of Finland",
        "duration_hours": 8.5,

        # Environmental conditions
        "wind_speed": 12.5,        # knots
        "wind_direction": 270,     # degrees
        "wave_height": 1.2,        # metres
        "wave_period": 5.5,        # seconds
        "current_speed": 0.8,      # knots
        "current_direction": 185,  # degrees
        "water_temperature": 8.5,  # °C
        "air_temperature": 6.0,
        "water_depth": 45.0,

        # Vessel condition
        "displacement": 250800,    # tonnes
        "draft_fore": 9.2,         # metres
        "draft_aft": 9.4,
        "time_since_dry_dock": 180,  # days

        # Predicted performance
        "predicted_speed": 22.5,
        "predicted_power": 45000,
        "predicted_fuel_consumption": 280,
        "predicted_rpm": 145,

        # Actual performance (measured)
        "actual_speed": 23.1,
        "actual_power": 44200,
        "actual_fuel_consumption": 275,
        "actual_rpm": 143,

        # Contract specifications
        "contract_speed": 22.0,
        "contract_power": 48000,
        "contract_fuel": 300,

        "notes": (
            "Excellent performance in moderate sea conditions. "
            "Vessel exceeded speed expectations while consuming less fuel than predicted."
        ),
    },
    {
        "trial_name": "Icon of the Seas – Sea Trial #2",
        "vessel_name": "Icon of the Seas",
        "trial_date": (datetime.now() - timedelta(days=15)).isoformat(),
        "status": "completed",
        "test_location": "Baltic Sea",
        "duration_hours": 12.0,

        "wind_speed": 18.0,
        "wind_direction": 315,
        "wave_height": 2.1,
        "wave_period": 6.8,
        "current_speed": 1.2,
        "current_direction": 200,
        "water_temperature": 7.8,
        "air_temperature": 4.5,
        "water_depth": 52.0,

        "displacement": 250800,
        "draft_fore": 9.3,
        "draft_aft": 9.3,
        "time_since_dry_dock": 195,

        "predicted_speed": 21.8,
        "predicted_power": 46500,
        "predicted_fuel_consumption": 295,
        "predicted_rpm": 148,

        "actual_speed": 21.5,
        "actual_power": 47100,
        "actual_fuel_consumption": 298,
        "actual_rpm": 150,

        "contract_speed": 22.0,
        "contract_power": 48000,
        "contract_fuel": 300,

        "notes": (
            "Performance within acceptable range despite higher sea state. "
            "Minor deviation in speed due to wave resistance."
        ),
    },
    {
        "trial_name": "Icon of the Seas – Speed Endurance Run",
        "vessel_name": "Icon of the Seas",
        "trial_date": (datetime.now() - timedelta(days=7)).isoformat(),
        "status": "in_progress",
        "test_location": "Baltic Sea",
        "duration_hours": 6.0,

        "wind_speed": 10.0,
        "wind_direction": 250,
        "wave_height": 0.9,
        "wave_period": 4.8,
        "current_speed": 0.5,
        "current_direction": 170,
        "water_temperature": 8.0,
        "air_temperature": 5.5,
        "water_depth": 60.0,

        "displacement": 250800,
        "draft_fore": 9.2,
        "draft_aft": 9.5,
        "time_since_dry_dock": 202,

        # Predicted (no actuals yet – trial is in progress)
        "predicted_speed": 22.8,
        "predicted_power": 45500,
        "predicted_fuel_consumption": 282,
        "predicted_rpm": 146,

        "contract_speed": 22.0,
        "contract_power": 48000,
        "contract_fuel": 300,

        "notes": "Speed endurance run in progress. Results pending.",
    },

    # ------------------------------------------------------------------
    # Star of the Seas
    # ------------------------------------------------------------------
    {
        "trial_name": "Star of the Seas – Initial Trial",
        "vessel_name": "Star of the Seas",
        "trial_date": (datetime.now() - timedelta(days=45)).isoformat(),
        "status": "completed",
        "test_location": "Gulf of Finland",
        "duration_hours": 10.0,

        "wind_speed": 8.5,
        "wind_direction": 180,
        "wave_height": 0.8,
        "wave_period": 4.2,
        "current_speed": 0.4,
        "current_direction": 160,
        "water_temperature": 10.2,
        "air_temperature": 12.5,
        "water_depth": 48.0,

        "displacement": 250800,
        "draft_fore": 9.1,
        "draft_aft": 9.2,
        "time_since_dry_dock": 30,   # brand new vessel

        "predicted_speed": 23.0,
        "predicted_power": 44800,
        "predicted_fuel_consumption": 278,
        "predicted_rpm": 146,

        "actual_speed": 23.8,
        "actual_power": 43900,
        "actual_fuel_consumption": 272,
        "actual_rpm": 144,

        "contract_speed": 22.0,
        "contract_power": 48000,
        "contract_fuel": 300,

        "notes": (
            "Outstanding performance in calm conditions. "
            "All parameters significantly better than predicted."
        ),
    },
    {
        "trial_name": "Star of the Seas – Rough Weather Trial",
        "vessel_name": "Star of the Seas",
        "trial_date": (datetime.now() - timedelta(days=20)).isoformat(),
        "status": "completed",
        "test_location": "North Baltic",
        "duration_hours": 9.0,

        "wind_speed": 22.0,
        "wind_direction": 330,
        "wave_height": 3.2,
        "wave_period": 8.1,
        "current_speed": 1.5,
        "current_direction": 220,
        "water_temperature": 7.2,
        "air_temperature": 3.0,
        "water_depth": 65.0,

        "displacement": 250800,
        "draft_fore": 9.4,
        "draft_aft": 9.5,
        "time_since_dry_dock": 55,

        "predicted_speed": 20.5,
        "predicted_power": 48500,
        "predicted_fuel_consumption": 310,
        "predicted_rpm": 152,

        "actual_speed": 20.1,
        "actual_power": 49200,
        "actual_fuel_consumption": 315,
        "actual_rpm": 154,

        "contract_speed": 22.0,
        "contract_power": 48000,
        "contract_fuel": 300,

        "notes": (
            "Heavy weather conditions. Speed below contract due to sea state – "
            "deemed acceptable per contract clause 4.2."
        ),
    },

    # ------------------------------------------------------------------
    # Utopia of the Seas
    # ------------------------------------------------------------------
    {
        "trial_name": "Utopia of the Seas – Acceptance Trial",
        "vessel_name": "Utopia of the Seas",
        "trial_date": (datetime.now() - timedelta(days=60)).isoformat(),
        "status": "completed",
        "test_location": "Baltic Sea",
        "duration_hours": 14.5,

        "wind_speed": 15.2,
        "wind_direction": 290,
        "wave_height": 1.8,
        "wave_period": 6.0,
        "current_speed": 0.9,
        "current_direction": 195,
        "water_temperature": 9.1,
        "air_temperature": 8.0,
        "water_depth": 55.0,

        "displacement": 236800,
        "draft_fore": 8.9,
        "draft_aft": 9.0,
        "time_since_dry_dock": 45,

        "predicted_speed": 22.2,
        "predicted_power": 43500,
        "predicted_fuel_consumption": 270,
        "predicted_rpm": 142,

        "actual_speed": 22.0,
        "actual_power": 44100,
        "actual_fuel_consumption": 273,
        "actual_rpm": 144,

        "contract_speed": 22.0,
        "contract_power": 46000,
        "contract_fuel": 285,

        "notes": "Met all contract specifications. Performance consistent with sister vessels.",
    },
    {
        "trial_name": "Utopia of the Seas – Fuel Economy Trial",
        "vessel_name": "Utopia of the Seas",
        "trial_date": (datetime.now() - timedelta(days=40)).isoformat(),
        "status": "completed",
        "test_location": "Gulf of Finland",
        "duration_hours": 16.0,

        "wind_speed": 6.0,
        "wind_direction": 90,
        "wave_height": 0.5,
        "wave_period": 3.5,
        "current_speed": 0.3,
        "current_direction": 100,
        "water_temperature": 9.8,
        "air_temperature": 9.0,
        "water_depth": 42.0,

        "displacement": 230000,
        "draft_fore": 8.7,
        "draft_aft": 8.8,
        "time_since_dry_dock": 65,

        "predicted_speed": 19.5,
        "predicted_power": 32000,
        "predicted_fuel_consumption": 210,
        "predicted_rpm": 128,

        "actual_speed": 19.8,
        "actual_power": 31500,
        "actual_fuel_consumption": 207,
        "actual_rpm": 126,

        "contract_speed": 19.0,
        "contract_power": 35000,
        "contract_fuel": 225,

        "notes": "Fuel economy run at reduced speed. Excellent efficiency – below predicted fuel burn.",
    },

    # ------------------------------------------------------------------
    # Upcoming / planned
    # ------------------------------------------------------------------
    {
        "trial_name": "Project Gemini – Builder's Trial",
        "vessel_name": "Project Gemini",
        "trial_date": (datetime.now() + timedelta(days=14)).isoformat(),
        "status": "planned",
        "test_location": "Gulf of Finland",
        "duration_hours": 8.0,

        # Vessel condition estimates
        "displacement": 245000,
        "draft_fore": 9.0,
        "draft_aft": 9.1,
        "time_since_dry_dock": 5,   # nearly new build

        # Predicted performance (design target)
        "predicted_speed": 23.5,
        "predicted_power": 46000,
        "predicted_fuel_consumption": 285,
        "predicted_rpm": 147,

        "contract_speed": 22.5,
        "contract_power": 48000,
        "contract_fuel": 295,

        "notes": "Builder's trial scheduled. Design targets based on sister-vessel data.",
    },
    {
        "trial_name": "Project Gemini – Acceptance Trial",
        "vessel_name": "Project Gemini",
        "trial_date": (datetime.now() + timedelta(days=45)).isoformat(),
        "status": "planned",
        "test_location": "Baltic Sea",
        "duration_hours": 12.0,

        "displacement": 245000,
        "draft_fore": 9.1,
        "draft_aft": 9.2,
        "time_since_dry_dock": 36,

        "predicted_speed": 23.2,
        "predicted_power": 45800,
        "predicted_fuel_consumption": 283,
        "predicted_rpm": 146,

        "contract_speed": 22.5,
        "contract_power": 48000,
        "contract_fuel": 295,

        "notes": "Full acceptance trial. Subject to weather window availability.",
    },
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def create_trials() -> None:
    """POST each trial to the API and print results."""
    endpoint = f"{API_BASE}/sea-trials"
    print(f"🚢  Seeding {len(sample_trials)} sea trials → {endpoint}\n")

    created, failed = 0, 0

    for trial in sample_trials:
        try:
            resp = requests.post(
                endpoint,
                json=trial,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if resp.status_code == 201:
                data = resp.json()
                created += 1
                score = data.get("overall_performance_score")
                score_str = f"  score={score:.1f}/100" if score else ""
                print(f"  ✅  [{data['sea_trial_id']:>3}]  {trial['trial_name']}{score_str}")
            else:
                failed += 1
                print(f"  ❌  {trial['trial_name']}")
                print(f"       HTTP {resp.status_code}: {resp.text[:200]}")
        except requests.exceptions.ConnectionError:
            print(
                "\n⛔  Cannot connect to the backend.\n"
                "    Start it first:  uvicorn app.main:app --reload\n"
            )
            sys.exit(1)
        except Exception as exc:
            failed += 1
            print(f"  ❌  {trial['trial_name']}: {exc}")

    print(f"\n{'─'*56}")
    print(f"  Created: {created}  |  Failed: {failed}  |  Total: {len(sample_trials)}")
    print(f"{'─'*56}")

    # Summary stats
    try:
        resp = requests.get(f"{API_BASE}/sea-trials/summary", timeout=5)
        if resp.status_code == 200:
            s = resp.json()
            avg = s.get("avg_performance_score")
            print(f"\n📊  DB Summary")
            print(f"    Total trials    : {s['total_trials']}")
            print(f"    Completed       : {s['completed_trials']}")
            print(f"    Avg performance : {f'{avg:.1f}/100' if avg else 'N/A'}")
            print(f"    Meet contract   : {s['trials_meeting_contract']}")
    except Exception:
        pass  # summary is optional


if __name__ == "__main__":
    print("\n" + "=" * 56)
    print("  Meyer Turku  –  Sea Trial Data Seeder  (v2)")
    print("=" * 56 + "\n")
    print("  Requires backend running on http://localhost:8000")
    print("  New fields: time_since_dry_dock, current_speed/direction\n")

    input("  Press Enter to seed data (Ctrl-C to abort) … ")
    print()

    create_trials()

    print("\n🎉  Done!  Open the Sea Trials tab in the dashboard to see the data.\n")
