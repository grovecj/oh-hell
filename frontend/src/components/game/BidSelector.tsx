import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface BidSelectorProps {
  validBids: number[];
  handSize: number;
  onBid: (bid: number) => void;
}

export default function BidSelector({ validBids, handSize, onBid }: BidSelectorProps) {
  const allBids = Array.from({ length: handSize + 1 }, (_, i) => i);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
    >
      <div className="rounded-xl bg-card border border-border p-6 shadow-2xl max-w-md w-full mx-4">
        <h3 className="text-xl font-bold text-center mb-1">Place Your Bid</h3>
        <p className="text-sm text-muted-foreground text-center mb-4">
          How many tricks will you win? ({handSize} card{handSize !== 1 ? 's' : ''} this round)
        </p>
        <div className="flex flex-wrap gap-2 justify-center">
          {allBids.map(bid => {
            const isValid = validBids.includes(bid);
            return (
              <button
                key={bid}
                onClick={() => isValid && onBid(bid)}
                disabled={!isValid}
                className={cn(
                  'h-12 w-12 rounded-lg text-lg font-bold transition-all',
                  isValid
                    ? 'bg-primary text-primary-foreground hover:bg-primary/90 hover:scale-110 cursor-pointer'
                    : 'bg-muted text-muted-foreground cursor-not-allowed opacity-50',
                )}
                title={!isValid ? 'Hook rule: this bid would make total bids equal tricks' : undefined}
              >
                {bid}
              </button>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}
