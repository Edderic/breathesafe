<template>
  <div class='question centered flex-dir-col'>
    <h3>{{question}}</h3>
    <input v-show="question_type == 'number'" type="number" :value="value" @change='send($event)' :disabled='disabled' class='number' :placeholder='placeholder'/>

    <div v-for="re in questionWithAnswerOptions" v-show="question_type == 'radio'" >
      <input type="radio" :id="re.questionAndAnswerOption" :value="re.answerOption" @change='send(re.answerOption)' :checked="isChecked(re.answerOption)" :disabled='disabled'/>
      <label :for="re.questionAndAnswerOption">{{re.answerOption}}</label>
    </div>
  </div>
</template>

<script>
import Button from './button.vue'
import { signIn } from './session.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';

export default {
  name: 'SurveyQuestion',
  components: {
    Button
  },
  data() {
    return {
    }
  },
  props: {
    value: Number,
    placeholder: String,
    question: String,
    question_type: {
      type: String,
      default: 'radio'
    },
    answer_options: {
      type: Array,
      default: []
    },
    selected: String,
    disabled: Boolean
  },
  computed: {
    questionWithAnswerOptions() {
      let collection = []
      for(let opt of this.answer_options) {
        collection.push(
          {
            'questionAndAnswerOption': this.question.replaceAll("?", "").replaceAll(" ", "-") + opt,
            'answerOption': opt
          }
        )

      }
      return collection
    }
  },
  async created() {
  },
  methods: {
    isChecked(re) {
      return this.selected == re
    },
    change(event) {
      this.$emit('update', { value: event.target.value })
    },
    send(args) {
      this.$emit('update', args)
    }
  }
}
</script>

<style scoped>
  .main {
    display: flex;
    flex-direction: column;
  }
  .flex-dir-col {
    display: flex;
    flex-direction: column;
  }
  p {

    margin: 1em;
  }

  .quote {
    font-style: italic;
    margin: 1em;
    margin-left: 2em;
    padding-left: 1em;
    border-left: 5px solid black;
    max-width: 25em;
  }
  .author {
    margin-left: 2em;
  }
  .credentials {
    margin-left: 3em;
  }

  .italic {
    font-style: italic;
  }

  .tagline {
    text-align: center;
    font-weight: bold;
  }

  .call-to-actions {
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 14em;
  }
  .call-to-actions a {
    text-decoration: none;
  }

  .main {
    display: grid;
    grid-template-columns: 100%;
    grid-template-rows: auto;
  }

  .centered {
    display: flex;
    justify-content: space-around;
  }

  img {
    width: 30em;
  }

  .question {
    padding-left: 1em;
  }

  @media(max-width: 700px) {
    img {
      width: 100vw;
    }

    .call-to-actions {
      height: 14em;
    }
  }

  .number {
    width: 5em;
  }
</style>
