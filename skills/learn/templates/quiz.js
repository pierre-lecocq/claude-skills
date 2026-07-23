/*
 * Shared quiz widget for /learn-generated sites.
 * Usage: <div class="quiz" data-quiz='[{"q":"...","choices":["...","..."],"answer":0,"explain":"..."}]'></div>
 * No dependencies; works from a file:// URL.
 */
(function () {
  function renderQuiz(container, quizIndex) {
    var questions;
    try {
      questions = JSON.parse(container.dataset.quiz);
    } catch (e) {
      container.textContent = "Quiz data could not be parsed.";
      return;
    }

    container.innerHTML = "";
    var results = new Array(questions.length).fill(null);

    questions.forEach(function (q, qi) {
      var block = document.createElement("div");
      block.className = "quiz-question";

      var prompt = document.createElement("p");
      prompt.className = "quiz-prompt";
      prompt.textContent = (qi + 1) + ". " + q.q;
      block.appendChild(prompt);

      var choicesEl = document.createElement("div");
      choicesEl.className = "quiz-choices";

      q.choices.forEach(function (choice, ci) {
        var id = "quiz-" + quizIndex + "-q" + qi + "-c" + ci;
        var label = document.createElement("label");
        label.className = "quiz-choice";
        label.setAttribute("for", id);

        var input = document.createElement("input");
        input.type = "radio";
        input.name = "quiz-" + quizIndex + "-q" + qi;
        input.id = id;
        input.value = String(ci);

        label.appendChild(input);
        label.appendChild(document.createTextNode(choice));
        choicesEl.appendChild(label);
      });

      block.appendChild(choicesEl);

      var feedback = document.createElement("div");
      feedback.className = "quiz-feedback";
      feedback.hidden = true;
      block.appendChild(feedback);

      choicesEl.addEventListener("change", function (e) {
        var chosen = Number(e.target.value);
        var correct = chosen === q.answer;
        results[qi] = correct;

        feedback.hidden = false;
        feedback.className = "quiz-feedback " + (correct ? "quiz-correct" : "quiz-incorrect");
        feedback.textContent = correct
          ? "Correct. " + (q.explain || "")
          : 'Not quite — correct answer: "' + q.choices[q.answer] + '". ' + (q.explain || "");

        Array.prototype.forEach.call(choicesEl.querySelectorAll("input"), function (i) {
          i.disabled = true;
        });

        updateScore();
      });

      container.appendChild(block);
    });

    var scoreEl = document.createElement("div");
    scoreEl.className = "quiz-score";
    container.appendChild(scoreEl);

    function updateScore() {
      var answered = results.filter(function (r) { return r !== null; }).length;
      var correct = results.filter(function (r) { return r === true; }).length;
      scoreEl.textContent = "Score: " + correct + "/" + answered + " answered (" + questions.length + " total)";
    }

    updateScore();
  }

  document.querySelectorAll(".quiz[data-quiz]").forEach(function (el, i) {
    renderQuiz(el, i);
  });
})();
