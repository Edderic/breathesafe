<template>
  <div>
    <h2 class='tagline'>Respirator User</h2>
    <div class='main'>
      <SurveyQuestion
        question="Which race or ethnicity best describes you?"
        :answer_options="race_ethnicity_options"
        @update="selectRaceEthnicity"
        :selected="raceEthnicity"
      />
      <SurveyQuestion
        question="What is your sex assigned at birth?"
        :answer_options="sex_assigned_at_birth_options"
        @update="selectSexAssignedAtBirth"
        :selected="sexAssignedAtBirth"
      />
    </div>

    <br>

    <Button text="Save" @click='saveAndGoTo("RespiratorUsers")'/>
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
          'raceEthnicity',
          'sexAssignedAtBirth'
        ]
    ),
  },
  async created() {
    await this.getCurrentUser()

    if (!this.currentUser) {
      signIn.call(this)
    } else {
      // TODO: a parent might input data on behalf of their children.
      // Currently, this.loadStuff() assumes We're loading the profile for the current user
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
    async saveAndGoTo(pathName) {
      await this.updateProfile()
      this.$router.push({
        name: pathName,
      })
    },
    selectRaceEthnicity(raceEth) {
      this.raceEthnicity = raceEth
    },
    selectSexAssignedAtBirth(sexAssignedAtBirth) {
      this.sexAssignedAtBirth = sexAssignedAtBirth
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
