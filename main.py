# =============================================================================

# Main entry point for the Project Zenith application.
# Its responsibilities are:
# 1. Check for necessary permissions (Administrator).
# 2. Instantiate and run the main application window from the frontend.
# =============================================================================

import sys
from optimizer_frontend import App
import optimizer_backend as backend

def main():
    """The main function to launch the application."""
    
    # It's highly recommended to run this as an administrator
    if not backend.is_admin():
        print("WARNING: Application not running as administrator.")
        print("Some features like cleaning system folders or managing startup may fail.")
        # In a real production app, you would show a popup and offer to relaunch as admin.
    
    # Create the main application window
    app = App()
    
    # Start the application's main loop
    app.mainloop()

if __name__ == "__main__":
    # This ensures the main() function is called only when the script is executed directly
    main()
