const FREE_LIMIT = 5
const COUNT_KEY = 'guest_message_count'

export function useGuestLimit() {
  const getCount = () => parseInt(sessionStorage.getItem(COUNT_KEY) || '0', 10)

  const increment = () => sessionStorage.setItem(COUNT_KEY, getCount() + 1)

  const reset = () => sessionStorage.removeItem(COUNT_KEY)

  const hasReachedLimit = () => getCount() >= FREE_LIMIT

  const remaining = () => Math.max(0, FREE_LIMIT - getCount())

  return { getCount, increment, reset, hasReachedLimit, remaining }
}