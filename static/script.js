// ==========================================
// GET ELEMENTS FROM HTML
// ==========================================

const researchButton =
    document.getElementById("researchButton");

const questionInput =
    document.getElementById("question");

const answerBox =
    document.getElementById("answer");

const sourceButtons =
    document.querySelectorAll(".source-button");

const pdfUpload =
    document.getElementById("pdfUpload");

const answerStatus =
    document.querySelector(".answer-status");


// ==========================================
// DEFAULT SOURCE
// ==========================================

let selectedSource = "pdf";


// ==========================================
// PDF / WEB / PDF + WEB SELECTION
// ==========================================

sourceButtons.forEach((button) => {

    button.addEventListener("click", () => {

        sourceButtons.forEach((btn) => {
            btn.classList.remove("active");
        });

        button.classList.add("active");

        selectedSource =
            button.dataset.source;

    });

});


// ==========================================
// MULTIPLE PDF UPLOAD
// ==========================================

if (pdfUpload) {

    pdfUpload.addEventListener(
        "change",
        async () => {

            const files =
                pdfUpload.files;


            if (files.length === 0) {
                return;
            }


            const formData =
                new FormData();


            // Add every selected PDF
            for (const file of files) {

                formData.append(
                    "files",
                    file
                );

            }


            answerBox.textContent =
                `Uploading ${files.length} PDF file(s)...`;


            if (answerStatus) {

                answerStatus.textContent =
                    "Uploading";

            }


            try {

                const response = await fetch(
                    "/upload",
                    {
                        method: "POST",
                        body: formData
                    }
                );


                const text =
                    await response.text();


                console.log(text);


                const data =
                    JSON.parse(text);


                if (!response.ok) {

                    throw new Error(
                        data.message ||
                        "PDF upload failed."
                    );

                }


                if (data.success) {

                    const cleanNames =
                        data.filenames.map((name) => {

                            let cleanName = name
                                .replace(/\.pdf$/i, "")
                                .replace(/^[a-f0-9]{20,}_/i, "")
                                .replace(/_/g, " ");

                            return cleanName;

                        });


                    const pdfList =
                        cleanNames
                            .map(
                                (name) => `📄 ${name}`
                            )
                            .join("<br>");


                    answerBox.innerHTML = `
                        <strong>PDFs uploaded successfully</strong>
                        <br><br>
                        ${pdfList}
                    `;


                    if (answerStatus) {

                        answerStatus.textContent =
                            "Uploaded";

                    }

                }

                else {

                    answerBox.textContent =
                        data.message;


                    if (answerStatus) {

                        answerStatus.textContent =
                            "Error";

                    }

                }

            }


            catch (error) {

                console.error(error);

                answerBox.textContent =
                    "Unable to upload PDF files.";


                if (answerStatus) {

                    answerStatus.textContent =
                        "Error";

                }

            }

        }
    );

}


// ==========================================
// RESEARCH BUTTON
// ==========================================

researchButton.addEventListener(
    "click",
    async () => {

        const question =
            questionInput.value.trim();


        if (question === "") {

            answerBox.textContent =
                "Please enter a research question.";

            return;
        }


        answerBox.textContent =
            "Researching... Please wait.";


        if (answerStatus) {

            answerStatus.textContent =
                "Researching";

        }


        researchButton.disabled = true;

        researchButton.textContent =
            "Researching...";


        try {

            const response =
                await fetch(
                    "/ask",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            question: question,
                            source: selectedSource
                        })
                    }
                );


            if (!response.ok) {

                throw new Error(
                    "Backend request failed."
                );

            }


            const data =
                await response.json();


            // Markdown -> formatted HTML
            if (
                typeof marked !== "undefined"
            ) {

                answerBox.innerHTML =
                    marked.parse(
                        data.answer
                    );

            }

            else {

                answerBox.textContent =
                    data.answer;

            }


            if (answerStatus) {

                answerStatus.textContent =
                    "Complete";

            }

        }


        catch (error) {

            console.error(error);

            answerBox.textContent =
                "Unable to generate an answer. Please try again.";


            if (answerStatus) {

                answerStatus.textContent =
                    "Error";

            }

        }


        finally {

            researchButton.disabled = false;

            researchButton.textContent =
                "Research";

        }

    }
);


// ==========================================
// CTRL + ENTER TO RESEARCH
// ==========================================

questionInput.addEventListener(
    "keydown",
    (event) => {

        if (
            event.ctrlKey &&
            event.key === "Enter"
        ) {

            researchButton.click();

        }

    }
);