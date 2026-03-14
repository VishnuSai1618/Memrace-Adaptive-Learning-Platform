import PyPDF2
import os
from werkzeug.utils import secure_filename

class PDFExtractor:
    """Service for extracting text from PDF files"""
    
    ALLOWED_EXTENSIONS = {'pdf'}
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in PDFExtractor.ALLOWED_EXTENSIONS
    
    @staticmethod
    def extract_text_from_pdf(file_path):
        """
        Extract text content from a PDF file
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text as string
            
        Raises:
            Exception: If PDF cannot be read or is corrupted
        """
        try:
            text_content = []
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    raise Exception("PDF is encrypted and cannot be read")
                
                # Extract text from each page
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text:
                        text_content.append(text)
                
                # Join all pages with newlines
                full_text = '\n\n'.join(text_content)
                
                # Clean up extra whitespace
                full_text = ' '.join(full_text.split())
                
                if not full_text.strip():
                    raise Exception("No text content found in PDF")
                
                return full_text
                
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    @staticmethod
    def save_uploaded_file(file, upload_folder='uploads'):
        """
        Save uploaded file to disk
        
        Args:
            file: FileStorage object from Flask request
            upload_folder: Directory to save file
            
        Returns:
            Path to saved file
        """
        try:
            # Create upload folder if it doesn't exist
            os.makedirs(upload_folder, exist_ok=True)
            
            # Secure the filename
            filename = secure_filename(file.filename)
            
            # Generate unique filename if needed
            file_path = os.path.join(upload_folder, filename)
            counter = 1
            base_name, extension = os.path.splitext(filename)
            
            while os.path.exists(file_path):
                filename = f"{base_name}_{counter}{extension}"
                file_path = os.path.join(upload_folder, filename)
                counter += 1
            
            # Save file
            file.save(file_path)
            
            return file_path
            
        except Exception as e:
            raise Exception(f"Error saving file: {str(e)}")
    
    @staticmethod
    def process_pdf_upload(file):
        """
        Complete workflow: save PDF and extract text
        
        Args:
            file: FileStorage object from Flask request
            
        Returns:
            Tuple of (file_path, extracted_text)
        """
        # Validate file
        if not file or file.filename == '':
            raise Exception("No file provided")
        
        if not PDFExtractor.allowed_file(file.filename):
            raise Exception("Invalid file type. Only PDF files are allowed")
        
        # Save file
        file_path = PDFExtractor.save_uploaded_file(file)
        
        # Extract text
        try:
            text = PDFExtractor.extract_text_from_pdf(file_path)
            return file_path, text
        except Exception as e:
            # Clean up file if extraction fails
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e
