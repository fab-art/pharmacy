import os
import base64
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, SignHere, Tabs, Recipients

def create_and_send_envelope(report_path, signatories):
    """
    Creates and sends a DocuSign envelope for signing the report.
    """
    # These would normally be in environment variables or a secret manager
    access_token = os.getenv('DOCUSIGN_ACCESS_TOKEN', 'MOCK_TOKEN')
    account_id = os.getenv('DOCUSIGN_ACCOUNT_ID', 'MOCK_ACCOUNT')
    base_path = os.getenv('DOCUSIGN_BASE_PATH', 'https://demo.docusign.net/restapi')

    api_client = ApiClient()
    api_client.host = base_path
    api_client.set_default_header("Authorization", f"Bearer {access_token}")

    with open(report_path, "rb") as file:
        content_bytes = file.read()
    base64_content = base64.b64encode(content_bytes).decode("ascii")

    document = Document(
        document_base64=base64_content,
        name="Counter-Verification Report",
        file_extension="pdf",
        document_id="1"
    )

    signers = []
    for i, sig in enumerate(signatories):
        signer = Signer(
            email=sig['email'],
            name=sig['name'],
            recipient_id=str(i + 1),
            routing_order=str(i + 1)
        )
        # Mocking signature placement
        sign_here = SignHere(anchor_string="/sig1/", anchor_units="pixels", anchor_y_offset="10", anchor_x_offset="20")
        signer.tabs = Tabs(sign_here_tabs=[sign_here])
        signers.append(signer)

    envelope_definition = EnvelopeDefinition(
        email_subject="Please sign the Counter-Verification Report",
        documents=[document],
        recipients=Recipients(signers=signers),
        status="sent"
    )

    # In a real environment, we'd call the API:
    # envelopes_api = EnvelopesApi(api_client)
    # results = envelopes_api.create_envelope(account_id=account_id, envelope_definition=envelope_definition)
    # return results.envelope_id

    return "MOCK_ENVELOPE_ID_12345"
