<template>
  <div>
    <h2 class='tagline'>Respirator User</h2>
    <div class='main'>
      <SurveyQuestion
        question="Which race or ethnicity best describes you?"
        :answer_options="race_ethnicity_options"
        @update="selectRaceEthnicity"
      />
    </div>

    <Button text="Save" @click='updateProfile'/>
  </div>
</template>

<script>
import Button from './button.vue'
import SurveyQuestion from './survey_question.vue'
import { signIn } from './session.js'
import { mapActions, mapWritableState, mapState } from 'pinia';
import { useProfileStore } from './stores/profile_store';
import { useMainStore } from './stores/main_store';

export default {
  name: 'RespiratorUser',
  components: {
    Button,
    SurveyQuestion
  },
  data() {
    return {
      race_ethnicity_question: "Which race or ethnicity best describes you?",
      race_ethnicity_options: [
        "American Indian or Alaskan Native",
        "Asian / Pacific Islander",
        "Black or African American",
        "Hispanic",
        "White / Caucasian",
        "Multiple ethnicity / Other",
        "Prefer not to disclose",
      ],
      sex_assigned_at_birth_question: "What is your sex assigned at birth?",
      sex_assigned_at_birth_options: [
        "Male",
        "Female",
        "Intersex",
        "Prefer Not To Disclose"
      ]
    }
  },
  props: {
  },
  computed: {
    ...mapState(
        useMainStore,
        [
          'currentUser',
        ]
    ),
    ...mapState(
        useProfileStore,
        [
          'profileId',
        ]
    ),
    ...mapWritableState(
        useProfileStore,
        [
          'firstName',
          'lastName',
          'raceEthnicity'
        ]
    ),
  },
  async created() {
    await this.getCurrentUser()

    if (!this.currentUser) {
      signIn.call(this)
    } else {
      this.loadStuff()
    }
  },
  methods: {
    ...mapActions(useMainStore, ['getCurrentUser']),
    ...mapActions(useProfileStore, ['loadProfile', 'updateProfile']),
    async loadStuff() {
      // TODO: load the profile for the current user
      await this.loadProfile()
    },
    selectRaceEthnicity(raceEth) {
      this.raceEthnicity = raceEth
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
  @media(max-width: 700px) {
    img {
      width: 100vw;
    }

    .call-to-actions {
      height: 14em;
    }
  }
</style>
