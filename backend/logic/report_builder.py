from fpdf import FPDF
from datetime import datetime

class CounterVerificationReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'RAMA Pharmacy Counter-Verification Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_report(case_id, case_data, analysis_results):
    """
    Generates a PDF report for a case.
    """
    pdf = CounterVerificationReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, f"Case ID: {case_id}", ln=True)
    pdf.cell(0, 10, f"Pharmacy: {case_data['pharmacy_id']}", ln=True)
    pdf.cell(0, 10, f"Date Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Summary of Findings", ln=True)
    pdf.set_font("Arial", size=12)

    total_deduction = 0
    for item in analysis_results:
        pdf.cell(0, 10, f"- {item['item']} ({item['line_id']}): {item['deduction']} RWF", ln=True)
        pdf.multi_cell(0, 5, f"  Reason: {item['reason']}")
        total_deduction += item['deduction']
        pdf.ln(2)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Total Agreed Deduction: {total_deduction} RWF", ln=True)

    pdf.ln(20)
    pdf.cell(0, 10, "Signatures:", ln=True)
    pdf.ln(10)
    pdf.cell(50, 10, "Manager Benefits: _________________")
    pdf.ln(10)
    pdf.cell(50, 10, "HoD RAMA: _________________")

    output_path = f"tests/sample_report_{case_id}.pdf"
    pdf.output(output_path)
    return output_path
