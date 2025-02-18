/*
  Copyright 2025 Jose Morales contact@josdem.io

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

package com.josdem.vetlog.advice;

import com.josdem.vetlog.exception.BusinessException;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.annotation.AfterThrowing;
import org.aspectj.lang.annotation.Aspect;
import org.springframework.stereotype.Component;

@Slf4j
@Aspect
@Component
public class AfterThrowingAdvice {

    @AfterThrowing(pointcut = "execution(* com.josdem.vetlog.service..**.*(..))", throwing = "ex")
    public void doRecoveryActions(RuntimeException ex) {
        log.info("Wrapping exception: " + ex.getMessage());
        throw new BusinessException(ex.getMessage(), ex);
    }
}
