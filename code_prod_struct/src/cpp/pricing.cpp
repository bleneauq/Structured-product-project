#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include "json_reader.hpp"
#include "Position.hpp"
#include "DataFeeder.hpp"
#include "Pricer.hpp"


int main(int argc, char **argv) {
    if (argc != 3) {
        std::cerr << "Wrong number of arguments. Exactly 2 arguments are required" << std::endl;
        std::exit(0);
    }
    std::ifstream ifsParams(argv[1]);
    nlohmann::json jsonParams = nlohmann::json::parse(ifsParams);

    PnlRng *rng = pnl_rng_create(PNL_RNG_MERSENNE);
    pnl_rng_sseed(rng, time(NULL));

    DataFeeder *dataFeeder = new DataFeeder(jsonParams);

    Pricer portfolio = Pricer(dataFeeder, rng);

    portfolio.writeResults(argv[2]);
    delete dataFeeder;
    pnl_rng_free(&rng);
    std::exit(0);
}