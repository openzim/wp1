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
public class CatVaccinationStrategy implements VaccinationStrategy {
    private static final String FVRCP = "FVRCP";
    private static final String DEWORMING = "Deworming";
    private static final String RABIES = "Rabies";

    private final VaccinationRepository vaccinationRepository;

    @Override
    public void vaccinate(Pet pet) {
        long weeks = ChronoUnit.WEEKS.between(pet.getBirthDate(), LocalDateTime.now());

        switch ((int) weeks) {
            case 0, 1, 2, 3, 4, 5, 6, 7, 8 -> log.info("No vaccination needed");
            case 9, 10, 11, 12 -> {
                log.info("First vaccination");
                registerVaccination(FVRCP, pet);
                registerVaccination(DEWORMING, pet);
            }
            case 13, 14, 15, 16 -> {
                log.info("Second vaccination");
                registerVaccination(FVRCP, pet);
                registerVaccination(DEWORMING, pet);
            }
            default -> {
                log.info("Annual vaccination");
                registerVaccination(FVRCP, pet);
                registerVaccination(DEWORMING, pet);
                registerVaccination(RABIES, pet);
            }
        }
    }

    private void registerVaccination(String name, Pet pet) {
        vaccinationRepository.save(new Vaccination(null, name, LocalDate.now(), VaccinationStatus.PENDING, pet));
    }
}
