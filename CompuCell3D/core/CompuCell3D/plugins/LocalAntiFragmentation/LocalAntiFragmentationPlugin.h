

#ifndef LOCALANTIFRAGMENTATIONPLUGIN_H

#define LOCALANTIFRAGMENTATIONPLUGIN_H



#include <CompuCell3D/CC3D.h>





#include "LocalAntiFragmentationDLLSpecifier.h"

#include <PublicUtilities/NumericalUtils.h>

class CC3DXMLElement;



namespace CompuCell3D {

    class Simulator;



    class Potts3D;

    class Automaton;

    //class AdhesionFlexData;

    class BoundaryStrategy;

    class ParallelUtilsOpenMP;

	class NumericalUtils;

    template <class T> class Field3D;

    template <class T> class WatchableField3D;



    class LOCALANTIFRAGMENTATION_EXPORT  LocalAntiFragmentationPlugin : public Plugin ,public EnergyFunction ,public CellGChangeWatcher {

        

    private:    

                        

        CC3DXMLElement *xmlData;        

        

        Potts3D *potts;

        

        Simulator *sim;

        

        ParallelUtilsOpenMP *pUtils;            

        

        ParallelUtilsOpenMP::OpenMPLock_t *lockPtr;        



        Automaton *automaton;



        BoundaryStrategy *boundaryStrategy;

        WatchableField3D<CellG *> *cellFieldG;

        

    public:



        LocalAntiFragmentationPlugin();

        virtual ~LocalAntiFragmentationPlugin();

        

                        



        

        //Energy function interface
        virtual double changeEnergy(const Point3D &pt, const CellG *newCell, const CellG *oldCell);        

        // CellChangeWatcher interface
        virtual void field3DChange(const Point3D &pt, CellG *newCell, CellG *oldCell);

                

        

        virtual void init(Simulator *simulator, CC3DXMLElement *_xmlData=0);



        virtual void extraInit(Simulator *simulator);



        //Steerrable interface

        virtual void update(CC3DXMLElement *_xmlData, bool _fullInitFlag=false);

        virtual std::string steerableName();

        virtual std::string toString();

		bool LocalAntiFragmentationPlugin::localConectivity_2D(Point3D * changePixel, Point3D * flipNeighbor);

    };

};

#endif


