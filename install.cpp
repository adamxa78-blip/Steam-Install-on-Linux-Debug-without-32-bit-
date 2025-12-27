#include <iostream>
#include <cstdlib>
#include <string>

int main() {
    std::cout << "Launching Steam Installer via Python..." << std::endl;

    // Command to execute the python script with sudo
    std::string command = "sudo python3 install_steam.py";

    // Execute the command
    int result = std::system(command.c_str());

    if (result == 0) {
        std::cout << "Process finished successfully." << std::endl;
    } else {
        std::cerr << "Process failed with exit code: " << result << std::endl;
    }

    return result;
}
