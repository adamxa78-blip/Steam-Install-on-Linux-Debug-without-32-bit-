#include <iostream>
#include <cstdlib>

int main() {
    std::cout << "Launching Steam Installer via Python..." << std::endl;
    
    // Command to execute the python script
    // Ensure install_steam.py is in the same directory
    int result = std::system("python3 install_steam.py");
    
    if (result == 0) {
        std::cout << "Python script finished successfully." << std::endl;
    } else {
        std::cerr << "An error occurred while running the Python script." << std::endl;
    }
    
    return result;
}
