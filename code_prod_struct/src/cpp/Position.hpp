#pragma once

#include "json_reader.hpp"
#include <list>
#include "MonteCarlo.hpp"
//#include "TimeGrid.hpp"

class Position {
public:
    PnlVect *deltas;
    PnlVect *deltasStdDev;
    double price;
    double priceStdDev;
    double flow;

    Position(double price, double priceStdDev, PnlVect* deltas, PnlVect* deltasStdDev, double flow);
    friend void to_json(nlohmann::json &j, const Position &positions);
    nlohmann::json print() const;
    ~Position();
};
