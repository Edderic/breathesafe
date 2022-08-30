
export function datetimeEnglish(datetime) {
  let dt = new Date(datetime)
  let options = { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' };
  let timeStringOptions = {hour: '2-digit', minute:'2-digit'}
  return `${dt.toLocaleDateString(undefined, options)} ${dt.toLocaleTimeString([], timeStringOptions)}`
}
