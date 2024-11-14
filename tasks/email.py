import mailbox
import email
import os
from email import generator
from pathlib import Path
from invoke import task


@task
def convert_mbox_to_eml(ctx, mbox_path, output_dir, log_attachments=True):
    """
    Convert an MBOX file to individual EML files, preserving all attachments.

    Args:
        mbox_path (str): Path to the source MBOX file
        output_dir (str): Directory where EML files will be saved
        log_attachments (bool): Whether to log information about attachments
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create a log file for attachments if requested
    if log_attachments:
        log_path = output_path / 'attachment_log.txt'
        log_file = open(log_path, 'w', encoding='utf-8')

    # Open the mbox file
    mbox = mailbox.mbox(mbox_path)

    # Iterate through all messages in the mbox
    for ix, message in enumerate(mbox):
        # Generate a unique filename for each email
        eml_filename = f"email_{ix + 1:06d}.eml"
        eml_path = output_path / eml_filename

        # Log attachment information if requested
        if log_attachments:
            log_file.write(f"\nEmail {ix + 1}: {eml_filename}\n")

            # Check for attachments
            attachment_count = 0
            pdf_count = 0

            for part in message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue

                filename = part.get_filename()
                if filename:
                    attachment_count += 1
                    if filename.lower().endswith('.pdf'):
                        pdf_count += 1
                    log_file.write(f"  - Attachment: {filename}\n")

            if attachment_count == 0:
                log_file.write("  No attachments found\n")
            else:
                log_file.write(f"  Total attachments: {attachment_count} (PDFs: {pdf_count})\n")

        # Write the message to an EML file
        with open(eml_path, 'w', encoding='utf-8') as eml_file:
            gen = generator.Generator(eml_file)
            gen.flatten(message)

        # Preserve original email date for the file
        if 'Date' in message:
            try:
                date_tuple = email.utils.parsedate_tz(message['Date'])
                if date_tuple:
                    timestamp = email.utils.mktime_tz(date_tuple)
                    os.utime(eml_path, (timestamp, timestamp))
            except Exception as e:
                print(f"Could not set timestamp for {eml_filename}: {e}")

    if log_attachments:
        log_file.close()

    print(f"Conversion complete. {ix + 1} emails extracted to {output_dir}")
    print(f"Check attachment_log.txt in the output directory for details about attachments")
