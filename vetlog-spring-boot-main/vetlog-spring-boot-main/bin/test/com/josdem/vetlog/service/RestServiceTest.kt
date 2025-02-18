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

package com.josdem.vetlog.service

import com.josdem.vetlog.command.MessageCommand
import com.josdem.vetlog.service.impl.RestServiceImpl
import okhttp3.ResponseBody
import org.junit.jupiter.api.BeforeEach
import org.mockito.Mock
import org.mockito.Mockito.mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.slf4j.LoggerFactory
import retrofit2.Call
import retrofit2.Retrofit
import java.io.IOException
import kotlin.test.Test

internal class RestServiceTest {
    private lateinit var service: RestServiceImpl

    @Mock
    private lateinit var retrofit: Retrofit

    companion object {
        private val log = LoggerFactory.getLogger(RestServiceTest::class.java)
    }

    @BeforeEach
    fun setup() {
        MockitoAnnotations.openMocks(this)
        service = RestServiceImpl(retrofit)
    }

    @Test
    @Throws(IOException::class)
    fun `Sending message`() {
        log.info("Running test: Sending message")
        val restService: RestService = mock()
        val messageCommand: MessageCommand = mock()
        val call: Call<ResponseBody> = mock()

        whenever(retrofit.create(RestService::class.java)).thenReturn(restService)
        whenever(restService.sendMessage(messageCommand)).thenReturn(call)

        service.setup()
        service.sendMessage(messageCommand)

        verify(call).execute()
    }
}