"""
Preloaded sample contracts representing the three core domains + a non-legal negative test,
matching the proposal walkthroughs (Section 6, 17, and Section 4.1).
"""

SAMPLE_CONTRACTS = {
    "lease_agreement": {
        "id": "sample-lease-01",
        "title": "Residential Lease Agreement (Real Estate)",
        "filename": "Rental_Agreement.pdf",
        "domain": "Real Estate Law and Property Transactions",
        "contract_type": "Lease Agreement",
        "description": "Demonstrates walkthrough in Section 17: Has one-sided termination, missing dispute resolution, and security deposit without refund timeline.",
        "text": """RESIDENTIAL LEASE AGREEMENT

This Residential Lease Agreement (the "Agreement") is made and entered into this 1st day of October, 2026, by and between Apex Property Holdings LLC ("Landlord"), and John Doe ("Tenant").

1. PREMISES
Landlord hereby leases to Tenant, and Tenant hereby leases from Landlord, the real property located at 452 Elm Street, Apartment 4B, City of Metropolis ("Premises"), for residential dwelling use only.

2. TERM AND DURATION
The term of this Lease shall commence on October 15, 2026, and shall terminate on October 14, 2027. This Agreement shall automatically renew for additional one-year terms unless either party gives notice.

3. RENT PAYMENT
Tenant shall pay to Landlord a monthly rent of $2,400.00, due on the first calendar day of each month. In the event rent is received after the 5th day of the month, Tenant shall pay a late fee equal to 10% of the overdue balance.

4. SECURITY DEPOSIT
Upon execution of this Lease, Tenant shall deposit with Landlord the sum of $4,800.00 as a Security Deposit. Landlord may deduct from the Security Deposit at its sole discretion for cleaning, repainting, or any breach of covenants. The remaining deposit, if any, shall be handled according to Landlord policies.

5. TERMINATION AND DEFAULT
Landlord may terminate this Lease immediately without cause upon providing 24 hours verbal or written notice to Tenant. In contrast, Tenant may only terminate this Lease upon 90 days prior written notice and payment of a 3-month rental cancellation penalty.

6. MAINTENANCE AND REPAIRS
Tenant shall be responsible for all repairs and routine maintenance of the Premises, including plumbing, electrical fixtures, and structural HVAC systems during the term of tenancy.

7. LIMITATION OF LIABILITY AND INDEMNITY
Tenant agrees to indemnify, defend, and hold harmless Landlord from any and all claims, liabilities, damages, or injuries occurring on the Premises, regardless of cause or Landlord's negligence. Landlord's aggregate liability under this agreement shall be zero.

8. GOVERNING LAW
This Agreement shall be governed by and construed in accordance with the laws of the State of New York.
"""
    },
    "nda_agreement": {
        "id": "sample-nda-01",
        "title": "Mutual Non-Disclosure Agreement (Commercial Law)",
        "filename": "Mutual_NDA_Standard.pdf",
        "domain": "Legal and Contract Law",
        "contract_type": "Non-Disclosure Agreement (NDA)",
        "description": "Commercial contract containing unilateral secrecy covenants, perpetual duration, and uncapped liability.",
        "text": """MUTUAL NON-DISCLOSURE AND PROPRIETARY INFORMATION AGREEMENT

This Agreement is entered into as of September 20, 2026, by and between Novatech Systems Inc. ("Company") and Global Partner Enterprises LLC ("Recipient").

1. DEFINITION OF CONFIDENTIAL INFORMATION
Confidential Information includes all technical data, trade secrets, software code, customer records, and commercial strategies disclosed by Company to Recipient, whether marked confidential or conveyed orally.

2. NON-DISCLOSURE OBLIGATIONS
Recipient agrees to hold Company's Confidential Information in strictest confidence and shall not disclose, reproduce, or distribute any part thereof to any third party without prior written consent.

3. TERM AND INDEFINITE DURATION
The obligations of confidentiality under this Agreement shall survive the termination of discussions and shall remain in effect in perpetuity without expiration date.

4. UNLIMITED LIABILITY AND REMEDIES
Recipient acknowledges that any breach causes irreparable harm. Recipient agrees to unlimited liability for all direct, indirect, punitive, and consequential damages arising from any disclosure.

5. RETURN OF MATERIALS
Within 5 business days of written request, Recipient shall return or certify destruction of all documents and electronic files containing Confidential Information.

6. DISPUTE RESOLUTION AND ARBITRATION
Any dispute arising out of or relating to this Agreement shall be finally settled by binding arbitration in San Francisco, California under the Commercial Arbitration Rules of the AAA.

7. GOVERNING LAW
This Agreement shall be governed by the laws of the State of California.
"""
    },
    "subcontractor_agreement": {
        "id": "sample-subcontract-01",
        "title": "Commercial Subcontractor Agreement (Construction Law)",
        "filename": "Subcontractor_Construction_Contract.pdf",
        "domain": "Construction Law and Contracts",
        "contract_type": "Subcontractor Agreement",
        "description": "Construction contract with liquidated delay damages, broad indemnification, and defects liability provisions.",
        "text": """CONSTRUCTION SUBCONTRACT AGREEMENT

This Subcontract Agreement is made on October 5, 2026, by and between BuildCorp Infrastructure Ltd. ("General Contractor") and Precision Masonry Works ("Subcontractor").

1. SCOPE OF WORK
Subcontractor agrees to furnish all labor, materials, equipment, and supervision necessary to complete the structural concrete and masonry package according to project engineering drawings and specifications.

2. PAYMENT AND RETENTION
General Contractor shall pay Subcontractor the total lump sum of $185,000.00 based on verified milestone progress certificates. A 10% retention money deduction shall be withheld until final defect liability clearance.

3. DELAY AND LIQUIDATED DAMAGES
Time is of the essence. If Subcontractor fails to achieve milestone completion dates, Subcontractor shall pay liquidated damages of $1,500.00 per day of delay until full handover.

4. DEFECTS LIABILITY
Subcontractor warrants all workmanship and materials for a defects liability period of 24 months following final project acceptance certificate.

5. INDEMNIFICATION AND HOLD HARMLESS
Subcontractor shall indemnify, defend, and hold harmless General Contractor and the Project Owner against any and all claims, damages, losses, or legal costs arising out of the performance of the Work, regardless of whether caused in part by General Contractor.

6. TERMINATION
General Contractor may terminate this Subcontract for convenience upon 7 days notice. Subcontractor may not terminate for any reason prior to project completion.

7. DISPUTE RESOLUTION
All construction disputes shall be referred to expedited mediation before the Construction Industry Arbitration Tribunal.
"""
    },
    "academic_paper": {
        "id": "sample-academic-01",
        "title": "Academic Research Paper (Negative Test - Screening Rejection)",
        "filename": "Neural_Attention_Survey_IEEE.pdf",
        "domain": "Non-Legal / Academic",
        "contract_type": "Academic Research Paper",
        "description": "Negative control sample: Demonstrates Section 4.1 Domain Screening rejection when an uploaded document is not a legal contract.",
        "text": """Deep Multi-Head Attention Mechanisms for Real-Time Visual Object Tracking: A Survey

Author: Dr. Elena Vance, Department of Computer Science, University of Technology
Published in IEEE Transactions on Pattern Analysis and Machine Intelligence, 2026.

ABSTRACT
Visual object tracking has undergone a transformative revolution with the advent of deep convolutional neural networks and transformer-based multi-head self-attention mechanisms. In this paper, we present a comprehensive benchmark across 45 publicly available tracking datasets. We formulate the tracking problem through cross-correlation and spatio-temporal token aggregation.

1. INTRODUCTION
Object tracking remains a fundamental problem in computer vision. Traditional methods relied on optical flow and handcrafted features such as HOG and color histograms. Modern frameworks instead leverage Siamese networks and spatio-temporal transformer attention blocks.

2. METHODOLOGY AND NETWORK ARCHITECTURE
Our proposed backbone extracts feature representations across multi-scale convolutional layers. Given a template image z and search image x, token embeddings are mapped into latent query, key, and value matrices. Softmax temperature scaling yields normalized attention weights.

3. EXPERIMENTAL RESULTS AND EVALUATION
We evaluated the architecture on the LaSOT and TrackingNet benchmarks. The experimental results show an average precision of 84.2% and success rate of 79.8% running at 65 frames per second on an NVIDIA RTX 4090 GPU.

4. CONCLUSION AND FUTURE WORK
This survey demonstrates the robustness of transformer tracking frameworks under occlusions and rapid illumination changes.

REFERENCES
[1] Vaswani, A., et al. "Attention Is All You Need." NeurIPS 2017.
[2] He, K., et al. "Deep Residual Learning for Image Recognition." CVPR 2016.
[3] Bertinetto, L., et al. "Fully-Convolutional Siamese Networks." ECCV 2016.
"""
    }
}
