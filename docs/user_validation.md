# User Validation & Persona Interaction Models

## 1. Academic Demo Personas
The system incorporates standardized fictional personas to demonstrate real-world role segregation, access control, and consent enforcement.

```
+-------------------------------------------------------------------------+
| PERSONA DIRECTORY & ACCESS ROLES                                        |
|                                                                         |
| Name       | Role Classification  | Associated Resident  | Permissions  |
|------------|----------------------|----------------------|--------------|
| Dharshini  | Administrator        | All Facility         | Full Admin   |
| Madhu      | Care Staff           | All Facility         | Staff Logs   |
| Kavi       | Primary Family       | Devi Raman (RES001)  | Full Consent |
| Charu      | Secondary Family     | Devi Raman (RES001)  | Partial      |
| Hema       | Emergency Contact    | Ramesh Sharma (002)  | Urgent Only  |
| Abi        | View-Only Contact    | Kamala Sundaram (003)| Revoked      |
| Mala       | Primary Family       | Mohan Patel (RES004) | Full Consent |
+-------------------------------------------------------------------------+
```

## 2. Resident Cohort Profiles

1. **Devi Raman (RES001)**
   - Age Group: 75–84
   - Independence Tier: *Needs Moderate Assistance*
   - Communication Style: *Brief & Timely*
   - Family Network: Daughter `Kavi` (Primary) and Son `Charu` (Secondary).

2. **Ramesh Sharma (RES002)**
   - Age Group: 85+
   - Independence Tier: *Needs High Assistance*
   - Communication Style: *Daily Summary*
   - Family Network: Daughter-in-law `Hema` (Emergency Contact).

3. **Kamala Sundaram (RES003)**
   - Age Group: 70–74
   - Independence Tier: *Needs Minimal Assistance*
   - Communication Style: *Weekly Digest*
   - Family Network: Niece `Abi` (View-Only Contact; Consent Revoked).

4. **Mohan Patel (RES004)**
   - Age Group: 75–84
   - Independence Tier: *Independent*
   - Communication Style: *Direct & Independent*
   - Family Network: Sister `Mala` (Primary Contact).

5. **Lakshmi Narayanan (RES005)**
   - Age Group: 80–84
   - Independence Tier: *Needs Moderate Assistance*
   - Communication Style: *Evening Recap*

---

## 3. Evaluator Walkthrough Guide

### Journey 1: Normal / Low Urgency (Devi Raman -> Kavi)
1. Navigate to **Care Events**. Notice `EVT001` (Devi participated in the music session with minimal assistance).
2. Click **Process Update** or select `EVT001` and `Kavi` in the **Communication** page.
3. Observe:
   - Role Check: Passed (Primary Contact).
   - Consent Check: Passed (Active Consent).
   - Safety Check: Passed (Non-medical facts).
   - Review Gate: Auto-Approved.
   - Family Summary: *"Your mother participated in the music session with minimal assistance."*
   - Internal Note: Segregated and suppressed from family view.

### Journey 2: Higher Urgency Operational Exception (Devi Raman -> Kavi)
1. Select `EVT002` (Devi declined mobility session due to fatigue; resting in room).
2. Click **Evaluate Pipeline**.
3. Observe:
   - System flags `urgency == 'High'` and `exception_flag == 1`.
   - Communication status sets to `Pending Review`.
4. Switch user to **Dharshini** or **Madhu** and visit **Review Queue**.
5. Click **Review & Decide**, add reviewer notes, and select **Approve**.
6. Switch back to **Kavi**; verified operational update is now released.

### Case 1: Revoked Consent (Kamala Sundaram -> Abi)
1. Trigger **Case 1** from the Dashboard or select `EVT003` with `Abi`.
2. Observe:
   - Consent status is `Revoked`.
   - Pipeline immediately halts.
   - Clear banner displayed: *"Information cannot be displayed because the current family member does not have permission to receive this update."*
   - No care facts or summaries are exposed.

### Case 3: Medical Language Interception (Ramesh Sharma -> Hema)
1. Select `EVT005` (Observation contains *"fever of 101F, suspected chest infection; staff administered paracetamol 500mg"*).
2. Pipeline detects clinical terminology.
3. Communication is diverted into the Review Queue to prevent medical boundary violations.

### Case 5: Family Medical Question Interception
1. Switch persona to **Hema** or **Kavi**.
2. Go to **Questions** page.
3. Type: *"What medication dosage should my mother take for her fever?"*
4. Notice immediate real-time warning banner above the form.
5. Click **Send Operational Inquiry**.
6. System tags inquiry as `Flagged Medical` and immediately responds with institutional operational boundary notice.
