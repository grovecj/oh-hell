import { Link } from 'react-router-dom'

export default function Rules() {
  return (
    <div className="min-h-screen p-8">
      <div className="mx-auto max-w-2xl">
        <div className="mb-8 flex items-center justify-between">
          <h1 className="text-3xl font-bold">How to Play</h1>
          <Link to="/" className="text-muted-foreground hover:text-foreground">
            Back to Home
          </Link>
        </div>

        <div className="space-y-6 text-foreground/90">
          <section>
            <h2 className="mb-2 text-xl font-semibold">Overview</h2>
            <p>
              Oh Hell is a trick-taking card game where the goal is to bid exactly the number of
              tricks you'll win each round. Bid correctly and score big — bid wrong and get nothing.
            </p>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold">Rounds</h2>
            <p>
              The number of cards dealt changes each round: 1, 2, 3, ... up to a maximum, then back
              down to 1. The maximum depends on the number of players (52 ÷ players, rounded down).
            </p>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold">Trump</h2>
            <p>
              After dealing, the top remaining card is flipped to determine the trump suit. Trump
              cards beat all other suits.
            </p>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold">Bidding</h2>
            <p>
              Starting left of the dealer, each player bids how many tricks they expect to win.
              The <strong>hook rule</strong> (optional): the dealer's bid cannot make the total bids
              equal the number of tricks — someone must be wrong.
            </p>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold">Playing</h2>
            <p>
              The player left of the dealer leads the first trick. You must follow the lead suit if
              you can. The highest trump played wins; if no trump, the highest card of the lead suit
              wins.
            </p>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold">Scoring</h2>
            <ul className="list-disc pl-6 space-y-1">
              <li><strong>Standard:</strong> +10 + bid if exact, 0 if miss</li>
              <li><strong>Progressive:</strong> +10 + bid² if exact, −|difference| if miss</li>
              <li><strong>Basic:</strong> +1 per trick + 10 bonus if exact</li>
            </ul>
          </section>
        </div>
      </div>
    </div>
  )
}
