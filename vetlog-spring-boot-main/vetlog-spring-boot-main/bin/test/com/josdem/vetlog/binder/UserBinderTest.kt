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

package com.josdem.vetlog.binder

import com.josdem.vetlog.command.UserCommand
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInfo
import org.slf4j.LoggerFactory

internal class UserBinderTest {

    val userBinder = UserBinder()

    companion object {
        val log = LoggerFactory.getLogger(UserBinderTest::class.java)
    }

    @Test
    fun `should bind user`(testInfo: TestInfo) {
        log.info(testInfo.displayName)

        val user = UserCommand().apply {
            username = "josdem"
            password = "12345678"
            firstname = "Jose"
            lastname = "Morales"
            countryCode = "+52"
            mobile = "1234567890"
            email = "contact@josdem.io"
        }

        val result = userBinder.bindUser(user)

        assertEquals("josdem", result.username)
        assertEquals(60, result.password.length)
        assertEquals("Jose", result.firstName)
        assertEquals("Morales", result.lastName)
        assertEquals("1234567890", result.mobile)
        assertEquals("+52", result.countryCode)
        assertEquals("contact@josdem.io", result.email)
    }

}