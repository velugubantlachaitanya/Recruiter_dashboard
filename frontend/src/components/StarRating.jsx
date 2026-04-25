export default function StarRating({ stars = 1, size = 'md' }) {
  const s = size === 'lg' ? 'text-2xl' : size === 'sm' ? 'text-sm' : 'text-lg'
  const colors = { 5:'text-emerald-400', 4:'text-blue-400', 3:'text-yellow-400', 2:'text-orange-400', 1:'text-red-400' }
  return (
    <span className={`${s} ${colors[stars] || 'text-gray-400'} tracking-wide`}>
      {'★'.repeat(stars)}{'☆'.repeat(5 - stars)}
    </span>
  )
}
