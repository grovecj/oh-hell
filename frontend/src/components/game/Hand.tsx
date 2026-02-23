import { motion, AnimatePresence } from 'framer-motion';
import Card from './Card';
import type { Card as CardType } from '@/types/game';

interface HandProps {
  cards: CardType[];
  validCards: CardType[];
  onPlayCard: (card: CardType) => void;
  isMyTurn: boolean;
  phase: string;
}

function isCardValid(card: CardType, validCards: CardType[]): boolean {
  return validCards.some(vc => vc.suit === card.suit && vc.rank === card.rank);
}

export default function Hand({ cards, validCards, onPlayCard, isMyTurn, phase }: HandProps) {
  const canPlay = isMyTurn && phase === 'playing';

  return (
    <div className="flex justify-center items-end py-4">
      <div className="flex gap-1 sm:gap-2">
        <AnimatePresence mode="popLayout">
          {cards.map((card, i) => {
            const valid = canPlay && isCardValid(card, validCards);
            return (
              <motion.div
                key={`${card.suit}-${card.rank}`}
                initial={{ opacity: 0, y: 50, rotateZ: -10 }}
                animate={{
                  opacity: 1,
                  y: 0,
                  rotateZ: (i - (cards.length - 1) / 2) * 3,
                }}
                exit={{ opacity: 0, y: -100, scale: 0.5 }}
                transition={{ duration: 0.3, delay: i * 0.05 }}
              >
                <Card
                  card={card}
                  onClick={() => valid && onPlayCard(card)}
                  disabled={!valid}
                  highlighted={valid}
                />
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
}
