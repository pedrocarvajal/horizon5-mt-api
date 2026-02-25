#include <ctime>
#include <iomanip>
#include <iostream>
#include <sstream>

#include "services/logger/headers/logger.hpp"
#include "services/logger/consts/color.hpp"

namespace services {
    Logger::Logger(
        const std::string prefix
    ) {
        this->prefix = prefix;
    }

    void Logger::info(
        const std::string message
    ) {
        std::cout << getFormattedMessage(enums::Level::INFO, message);
    }

    void Logger::error(
        const std::string message
    ) {
        std::cout << getFormattedMessage(enums::Level::ERROR, message);
    }

    void Logger::success(
        const std::string message
    ) {
        std::cout << getFormattedMessage(enums::Level::SUCCESS, message);
    }

    void Logger::warning(
        const std::string message
    ) {
        std::cout << getFormattedMessage(enums::Level::WARNING, message);
    }

    std::string Logger::getFormattedMessage(
        enums::Level severity,
        const std::string message
    ) {
        return getTime() +
               " " + getLevel(severity) +
               " " + getPrefix() +
               " > " +
               message +
               "\n";
    }

    std::string Logger::getTime() {
        std::time_t now = std::time(nullptr);
        std::tm *localtime = std::localtime(&now);
        std::ostringstream stream;
        stream << std::put_time(localtime, "%Y-%m-%d %H:%M:%S");

        return "[" + stream.str() + "]";
    }

    std::string Logger::getLevel(enums::Level severity) {
        if (severity == enums::Level::INFO)
            return consts::color::WHITE + "[INF]" + consts::color::RESET;

        if (severity == enums::Level::WARNING)
            return consts::color::YELLOW + "[WAR]" + consts::color::RESET;

        if (severity == enums::Level::SUCCESS)
            return consts::color::GREEN + "[SUC]" + consts::color::RESET;

        if (severity == enums::Level::ERROR)
            return consts::color::RED + "[ERR]" + consts::color::RESET;

        return "";
    }

    std::string Logger::getPrefix() {
        if (!prefix.empty())
            return "[" + prefix + "]";

        return "";
    }
}
