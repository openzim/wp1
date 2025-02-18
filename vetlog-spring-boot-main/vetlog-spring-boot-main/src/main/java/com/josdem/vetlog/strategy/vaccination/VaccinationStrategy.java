package com.josdem.vetlog.strategy.vaccination;

import com.josdem.vetlog.model.Pet;

public interface VaccinationStrategy {
    void vaccinate(Pet pet);
}
