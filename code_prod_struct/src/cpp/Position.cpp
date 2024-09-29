#include <iostream>
#include "Position.hpp"

Position::Position(double price, double priceStdDev, PnlVect* deltas, PnlVect* deltasStdDev, double flow)
    : price(price), priceStdDev(priceStdDev), deltas(deltas), deltasStdDev(deltasStdDev), flow(flow) {}

void to_json(nlohmann::json &j, const Position &position) {
    j["price"] = position.price;
    j["priceStdDev"] = position.priceStdDev;
    j["deltas"] = position.deltas;
    j["deltasStdDev"] = position.deltasStdDev;
    j["flux"] = position.flow;
}

nlohmann::json Position::print() const {
    nlohmann::json j = *this;
    return j;
}

Position::~Position() {
    pnl_vect_free(&deltas);
    pnl_vect_free(&deltasStdDev);
}
