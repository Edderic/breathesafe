export async function signIn() {
  if (!this.currentUser) {
    let query = JSON.parse(JSON.stringify(this.$route.query))

    query['attempt-name'] = this.$route.name

    for (let k in this.$route.params) {
      query[`params-${k}`] = this.$route.params[k]
    }

    await this.$router.push({
      name: 'SignIn',
      query: query
    })
  }
}
