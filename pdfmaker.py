from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

def create_medical_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Content structure: Topic Name and the Text Body
    content = [
        ("Section 1: Anatomy of the Human Heart", 
         "The human heart is a muscular organ roughly the size of a closed fist. It is divided into four chambers: the right atrium, the right ventricle, the left atrium, and the left ventricle. The atria are the receiving chambers, while the ventricles are the discharging chambers. The septum is a thick muscular wall that separates the left and right sides of the heart, preventing the mixing of oxygenated and deoxygenated blood. Valves, such as the tricuspid and mitral valves, ensure one-way blood flow and prevent backflow during contractions."),
        
        ("Section 2: Blood Vessel Architecture", 
         "The circulatory system relies on three primary types of vessels: arteries, veins, and capillaries. Arteries carry oxygenated blood away from the heart at high pressure; they have thick, elastic walls to withstand this force. The aorta is the largest artery in the body. Veins return deoxygenated blood to the heart and contain valves to prevent blood from flowing backward due to gravity. Capillaries are microscopic vessels where the exchange of oxygen, nutrients, and waste products occurs between the blood and tissues through thin, permeable walls."),
        
        ("Section 3: Blood Composition and Function", 
         "Blood is a fluid connective tissue consisting of plasma, red blood cells (erythrocytes), white blood cells (leukocytes), and platelets (thrombocytes). Erythrocytes contain hemoglobin, a protein that binds to oxygen for transport. Leukocytes are the primary cells of the immune system, defending the body against pathogens. Platelets are cell fragments essential for blood clotting and wound healing. Plasma, the liquid component, carries dissolved proteins, glucose, mineral ions, hormones, and carbon dioxide."),
        
        ("Section 4: The Cardiac Cycle and Pulse", 
         "The cardiac cycle refers to the complete sequence of events from the beginning of one heartbeat to the beginning of the next. It includes diastole (relaxation phase) and systole (contraction phase). During atrial systole, the atria contract to push blood into the ventricles. During ventricular systole, the ventricles contract to pump blood into the lungs and the rest of the body. The 'lub-dub' sound heard through a stethoscope is caused by the closing of the heart valves. Heart rate is regulated by the sinoatrial (SA) node, often called the natural pacemaker.")
    ]

    y_position = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, y_position, "Comprehensive Guide: The Circulatory System")
    y_position -= 40

    for title, body in content:
        # Title
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, title)
        y_position -= 20
        
        # Body text with wrapping
        c.setFont("Helvetica", 11)
        lines = simpleSplit(body, "Helvetica", 11, width - 100)
        for line in lines:
            if y_position < 50: # Start new page if out of space
                c.showPage()
                y_position = height - 50
                c.setFont("Helvetica", 11)
            c.drawString(50, y_position, line)
            y_position -= 15
        y_position -= 20 # Space between sections

    c.save()
    print(f"Successfully created {filename}")

if __name__ == "__main__":
    create_medical_pdf("circulatory_system_study.pdf")