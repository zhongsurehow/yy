from src.game import Game

def main():
    """
    Main entry point for running a simulation of the Tianji Bian game engine.
    """
    print("=============================================")
    print("===   Tianji Bian - Game Engine Prototype ===")
    print("=============================================")

    try:
        player_names = ["Player 1 (Alice)", "Player 2 (Bob)", "Player 3 (Charlie)"]

        # Define the path to the unzipped assets directory
        assets_path = "tianji-fix-data-and/assets"

        # We can define a specific scenario to test
        test_cards_to_play = ["basic_14_da_you", "basic_21_shi_he", "basic_12_pi"]

        game = Game(player_names=player_names, assets_path_str=assets_path)

        # Setup the game, injecting the test cards into players' hands
        game.setup(test_cards=test_cards_to_play)

        print("\n--- Initial Player States ---")
        for p in game.game_state.players:
            print(f"  - {p}")

        # Run the simulation for a couple of turns
        game.run(num_turns=2)

    except FileNotFoundError as e:
        print(f"\nFATAL ERROR: {e}. Make sure the assets directory exists at '{assets_path}'.")
    except Exception as e:
        print(f"\nAn unexpected error occurred during the simulation: {e}")

if __name__ == '__main__':
    main()