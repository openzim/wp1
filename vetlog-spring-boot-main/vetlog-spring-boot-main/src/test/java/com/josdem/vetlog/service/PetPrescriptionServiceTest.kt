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

import com.josdem.vetlog.client.GoogleStorageWriter
import com.josdem.vetlog.command.PetLogCommand
import com.josdem.vetlog.service.impl.PetPrescriptionServiceImpl
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.any
import org.mockito.kotlin.eq
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.slf4j.LoggerFactory
import org.springframework.test.util.ReflectionTestUtils
import org.springframework.web.multipart.MultipartFile
import java.io.IOException
import java.io.InputStream

internal class PetPrescriptionServiceTest {

    private lateinit var service: PetPrescriptionService

    @Mock
    private lateinit var googleStorageWriter: GoogleStorageWriter

    companion object {
        private val log = LoggerFactory.getLogger(PetPrescriptionServiceTest::class.java)
    }

    @BeforeEach
    fun setup() {
        MockitoAnnotations.openMocks(this)
        service = PetPrescriptionServiceImpl(googleStorageWriter)

        // Manually set the `bucket` field using ReflectionTestUtils to avoid null issues in tests.
        ReflectionTestUtils.setField(service, "bucket", "test-bucket")
    }

    @Test
    @Throws(IOException::class)
    fun `Saving a pet image`() {
        log.info("Running test: Saving a pet image")

        val petLogCommand = PetLogCommand()
        val multiPartFile: MultipartFile = mock()
        val inputStream: InputStream = mock()

        whenever(inputStream.available()).thenReturn(1000)
        whenever(multiPartFile.inputStream).thenReturn(inputStream)

        petLogCommand.attachment = multiPartFile // Kotlin のプロパティアクセスに修正

        service.attachFile(petLogCommand)

        verify(googleStorageWriter).uploadToBucket(
            any(),
            any(),
            eq(inputStream),
            any()
        )
    }
}

