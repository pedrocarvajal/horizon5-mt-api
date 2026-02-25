#pragma once

#include <string>
#include "services/logger/enums/level.hpp"

namespace services {
    class Logger {
    private:
        std::string prefix;

    public:
        Logger(const std::string prefix = "");
        void info(const std::string message);
        void error(const std::string message);
        void success(const std::string message);
        void warning(const std::string message);

    private:
        std::string getFormattedMessage(
            enums::Level severity,
            const std::string message
        );
        std::string getTime();
        std::string getLevel(enums::Level severity);
        std::string getPrefix();
    };
}
