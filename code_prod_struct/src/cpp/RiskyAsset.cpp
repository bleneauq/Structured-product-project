#include "RiskyAsset.hpp"

RiskyAsset::RiskyAsset(double spot, double drift, PnlVect *volatilityVector)
    : spot_(spot), drift_(drift) {
        volatilityVector_ = pnl_vect_create_from_zero(volatilityVector->size);
        pnl_vect_clone(volatilityVector_, volatilityVector);
    }

RiskyAsset::RiskyAsset(const RiskyAsset &that) {
	this->spot_ = that.spot_;
	this->drift_ = that.drift_;
	this->volatilityVector_ = pnl_vect_copy(that.volatilityVector_);
}

RiskyAsset::~RiskyAsset() {
    pnl_vect_free(&volatilityVector_);
}