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

  // Card width is 156px (lg size). Overlap cards like holding them in a hand.
  // Show ~40px of each card except the last, clamped so hand fits on screen.
  const cardWidth = 156;
  const maxHandWidth = typeof window !== 'undefined' ? window.innerWidth - 40 : 1200;
  const desiredExposed = 40; // px of each card visible behind the next
  const desiredMargin = -(cardWidth - desiredExposed);
  // Make sure the hand still fits: total width = cardWidth + (n-1) * (cardWidth + margin)
  const handWidth = cardWidth + (cards.length - 1) * (cardWidth + desiredMargin);
  const marginRight = handWidth <= maxHandWidth
    ? desiredMargin
    : -((cards.length * cardWidth - maxHandWidth) / (cards.length - 1 || 1));

  return (
    <div className="flex justify-center items-end py-4">
      <div className="flex">
        <AnimatePresence mode="popLayout">
          {cards.map((card, i) => {
            const valid = canPlay && isCardValid(card, validCards);
            // Fan arc: center card is highest, edges dip down
            const center = (cards.length - 1) / 2;
            const offset = i - center;
            const rotation = offset * 4;
            const arcY = Math.abs(offset) * Math.abs(offset) * 4;
            return (
              <motion.div
                key={`${card.suit}-${card.rank}`}
                initial={{ opacity: 0, y: 50, rotateZ: -10 }}
                animate={{
                  opacity: 1,
                  y: arcY,
                  rotateZ: rotation,
                }}
                exit={{ opacity: 0, y: -100, scale: 0.5 }}
                transition={{ duration: 0.3, delay: i * 0.05 }}
                style={{
                  marginRight: i < cards.length - 1 ? marginRight : 0,
                  zIndex: i,
                  transformOrigin: 'bottom center',
                }}
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
