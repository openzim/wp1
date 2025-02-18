package com.josdem.vetlog.strategy.vaccination.impl;

import com.josdem.vetlog.enums.VaccinationStatus;
import com.josdem.vetlog.model.Pet;
import com.josdem.vetlog.model.Vaccination;
import com.josdem.vetlog.repository.VaccinationRepository;
import com.josdem.vetlog.strategy.vaccination.VaccinationStrategy;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class DogVaccinationStrategy implements VaccinationStrategy {

    private static final String DA2PP = "DA2PP";
    private static final String DEWORMING = "Deworming";
    private static final String LEPTOSPIROSIS = "Leptospirosis";
    private static final String RABIES = "Rabies";

    private final VaccinationRepository vaccinationRepository;

    @Override
    public void vaccinate(Pet pet) {
        Long weeks = ChronoUnit.WEEKS.between(pet.getBirthDate(), LocalDateTime.now());

        switch (weeks.intValue()) {
            case 0, 1, 2, 3, 4, 5, 6, 7, 8 -> log.info("No vaccination needed");
            case 9, 10, 11, 12 -> {
                log.info("First vaccination");
                registerVaccination(DA2PP, pet);
                registerVaccination(DEWORMING, pet);
            }
            case 13, 14, 15, 16 -> {
                log.info("Second vaccination");
                registerVaccination(DA2PP, pet);
                registerVaccination(DEWORMING, pet);
                registerVaccination(LEPTOSPIROSIS, pet);
            }
            default -> {
                log.info("Annual vaccination");
                registerVaccination(DA2PP, pet);
                registerVaccination(DEWORMING, pet);
                registerVaccination(LEPTOSPIROSIS, pet);
                registerVaccination(RABIES, pet);
                registerVaccination("Canine influenza", pet);
            }
        }
    }

    private void registerVaccination(String name, Pet pet) {
        vaccinationRepository.save(new Vaccination(null, name, LocalDate.now(), VaccinationStatus.PENDING, pet));
    }
}
